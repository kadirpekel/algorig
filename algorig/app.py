import sys
import base64
import logging
import importlib
import json

from pyteal import compileTeal, Mode, Approve

from algosdk.v2client import algod
from algosdk import kmd
from algosdk.logic import get_application_address
from algosdk.transaction import (assign_group_id,
                                 Transaction,
                                 ApplicationCallTxn,
                                 OnComplete,
                                 StateSchema,
                                 LogicSigTransaction,
                                 LogicSig)


from algorig.config import load_config, save_config


logger = logging.getLogger(__name__)

APP_MODULE_NAME = 'protocol'
APP_FILE_NAME = f'{APP_MODULE_NAME}.py'
APP_TEMPLATE = '''from pyteal import *

from algorig.app import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):
        # Implement your contract here using pyteal
        return Int(1)

    def op_example_command(self, my_str: str, my_int: int = 42):
        # This is an example method which can be used as cli command
        print(f'my_str: {my_str}, my_int: {my_int}')
'''


def init_application_stub():
    with open(APP_FILE_NAME, 'w') as f:
        f.write(APP_TEMPLATE)


class BaseApplication:

    DEFAULT_WAIT_TIMEOUT = 10
    ZERO_ADDRESS = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ'

    @classmethod
    def load_from_cwd(cls):
        sys.path.insert(0, '.')
        protocol = importlib.import_module(APP_MODULE_NAME)
        Application = getattr(protocol, 'Application', None)
        assert Application, '`Application` class not found'
        assert issubclass(Application, BaseApplication),\
            '`Application` should be a subclass of `BaseApplication`'

        return Application()

    def generate_commands(self):
        from komandr import command

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr_name.startswith('op_') and callable(attr):
                command(name=attr_name[3:])(attr)

    def __init__(self):
        self.config = load_config()
        self.kmd = self.build_kmd()
        self.algod = self.build_algod()
        self.suggested_params = self.algod.suggested_params()

    def decode_state(self, state):
        formatted = {}
        for item in state:
            key = item['key']
            value = item['value']
            formatted_key = base64.b64decode(key).decode('utf-8')
            if value['type'] == 1:
                # byte string
                if formatted_key == 'voted':
                    formatted_value = \
                        base64.b64decode(value['bytes']).decode('utf-8')
                else:
                    formatted_value = value['bytes']
                formatted[formatted_key] = formatted_value
            else:
                # integer
                formatted[formatted_key] = value['uint']
        return formatted

    def fetch_app_info(self):
        return self.algod.application_info(self.config['app_id'])

    def wait_for_transaction(self, tx_id):
        last_round = self.algod.status().get('last-round')
        txinfo = self.algod.pending_transaction_info(tx_id)
        print(f'Processing transaction: {tx_id}, please wait...')
        while not (txinfo.get('confirmed-round') and
                   txinfo.get('confirmed-round') > 0):
            last_round += 1
            self.algod.status_after_block(last_round)
            txinfo = self.algod.pending_transaction_info(tx_id)
        print('Confirmed at round: {}'.format(txinfo.get('confirmed-round')))
        return txinfo

    def compile_program(self, program, is_logicsig=False):
        mode = Mode.Signature if is_logicsig else Mode.Application
        return compileTeal(program,
                           mode=mode,
                           version=self.config['teal_version'])

    def compile_teal(self, teal):
        meta = self.algod.compile(teal)
        return meta['result']

    def get_wallet_token(self):
        entries = self.kmd.list_wallets()
        wallet_name = self.config['wallet_name']
        for entry in entries:
            if entry['name'] == wallet_name:
                wallet_token = entry['id']
                return wallet_token

        raise ValueError(f'Wallet `{wallet_name}` not found on KMD')

    def sign_transaction(self, txn):


        if not isinstance(txn, Transaction):
            return txn

        if isinstance(txn, LogicSigTransaction):
            return txn

        wallet_password = self.config['wallet_password']
        wallet_token = self.get_wallet_token()
        wallet_handle = self.kmd.init_wallet_handle(wallet_token,
                                                    wallet_password)
        signed_txn = self.kmd.sign_transaction(wallet_handle,
                                               wallet_password,
                                               txn)
        self.kmd.release_wallet_handle(wallet_handle)
        return signed_txn

    def sign_bytecode(self, bytecode, address=None, arg=None):
        wallet_password = self.config['wallet_password']
        wallet_token = self.get_wallet_token()
        wallet_handle = self.kmd.init_wallet_handle(wallet_token,
                                                    wallet_password)
        result = self.kmd.kmd_request('POST', '/program/sign', data={
            'data': bytecode,
            'address': address or self.config['signing_address'],
            'wallet_handle_token': wallet_handle,
            'wallet_password': wallet_password,
        })
        logicsig = LogicSig(base64.b64decode(bytecode), arg)
        logicsig.sig = result['sig']
        return logicsig

    def build_algod(self):
        return algod.AlgodClient(self.config['algod_token'],
                                 self.config['algod_address'])

    def build_kmd(self):
        return kmd.KMDClient(self.config['kmd_token'],
                             self.config['kmd_address'])

    def get_approval_program_as_teal(self):
        return self.compile_program(self.get_approval_program())

    def get_clear_state_program_as_teal(self):
        return self.compile_program(self.get_clear_state_program())

    def get_approval_program_bytecode(self):
        return base64.b64decode(
            self.compile_teal(self.get_approval_program_as_teal()))

    def get_clear_state_program_bytecode(self):
        return base64.b64decode(
            self.compile_teal(self.get_clear_state_program_as_teal()))

    def get_global_schema(self):
        return StateSchema(
            num_uints=self.config['num_global_ints'],
            num_byte_slices=self.config['num_global_byte_slices'])

    def get_local_schema(self):
        return StateSchema(
            num_uints=self.config['num_local_ints'],
            num_byte_slices=self.config['num_local_byte_slices'])

    def build_app_call_txn(self, **kwargs):

        is_application_create = kwargs.pop('is_application_create', False)
        app_id = self.config.get('app_id', 0)

        if is_application_create:
            assert app_id == 0, 'Application already created.'
        else:
            assert app_id > 0, 'Application not created yet.'

        def to_ints(self, *args):
            return [int(arg) for arg in args]

        kwargs.setdefault('sender', self.config['signing_address'])
        kwargs.setdefault('sp', self.suggested_params)
        kwargs.setdefault('on_complete', OnComplete.NoOpOC)
        kwargs.setdefault('index', app_id)
        kwargs.setdefault('accounts',
                          to_ints(self.config.get('accounts', [])))
        kwargs.setdefault('foreign_apps',
                          to_ints(self.config.get('foreign_apps', [])))
        kwargs.setdefault('foreign_assets',
                          to_ints(self.config.get('foreign_assets', [])))
        return ApplicationCallTxn(**kwargs)

    def op_create(self, app_args: list = []):
        response = self.submit(self.build_app_call_txn(
            approval_program=self.get_approval_program_bytecode(),
            clear_program=self.get_clear_state_program_bytecode(),
            global_schema=self.get_global_schema(),
            local_schema=self.get_local_schema(),
            app_args=app_args or [],
            is_application_create=True
        ))
        app_id = response['application-index']
        app_address = get_application_address(app_id)
        self.config.update({
            'app_id': app_id,
            'app_address': app_address
        })
        save_config(self.config)
        print(f'Application created with id: {app_id}.')
        return response

    def op_update(self, app_args: list = []):
        response = self.submit(self.build_app_call_txn(
            on_complete=OnComplete.UpdateApplicationOC,
            approval_program=self.get_approval_program_bytecode(),
            clear_program=self.get_clear_state_program_bytecode(),
            app_args=app_args or []
        ))
        print('Application updated successfully.')
        return response

    def op_delete(self):
        response = self.submit(self.build_app_call_txn(
            on_complete=OnComplete.DeleteApplicationOC,
        ))
        del self.config['app_id']
        del self.config['app_address']
        save_config(self.config)
        print('Application deleted successfully.')
        return response

    def op_clearstate(self, sender):
        response = self.submit(self.build_app_call_txn(
            on_complete=OnComplete.ClearStateOC,
            sender=sender
        ))
        print('Application cleared state successfully.')
        return response

    def op_closeout(self, sender):
        response = self.submit(self.build_app_call_txn(
            on_complete=OnComplete.CloseOutOC,
            sender=sender
        ))
        print('Application closed out successfully.')
        return response

    def op_optin(self, sender):
        response = self.submit(self.build_app_call_txn(
            on_complete=OnComplete.OptInOC,
            sender=sender
        ))
        print('Application opted in successfully.')
        return response

    def op_dump_teal(self, clear_state=False):
        if clear_state:
            print(self.get_clear_state_program())
        else:
            print(self.get_approval_program_as_teal())

    def read_global_state(self):
        app_info = self.fetch_app_info()
        state = app_info["params"].get('global-state', {})
        return self.decode_state(state)

    def read_local_state(self, address):
        account_info = self.algod.account_info(address)
        assert account_info, 'Account not found'
        apps = account_info.get('apps-local-state', [])
        for app in apps:
            if app['id'] == self.config.get('app_id'):
                state = app['key-value']
                return self.decode_state(state)
        return {}

    def op_global_state(self):
        print(json.dumps(self.read_global_state(), indent=2))

    def op_local_state(self, address):
        print(json.dumps(self.read_local_state(address), indent=2))

    def submit_group(self, transactions):
        assign_group_id(transactions)
        signed_transactions = []
        for txn in transactions:
            signed_txn = self.sign_transaction(txn)
            signed_transactions.append(signed_txn)

        tx_id = self.algod.send_transactions(signed_transactions)
        return self.wait_for_transaction(tx_id)

    def submit(self, txn):
        signed_txn = self.sign_transaction(txn)
        tx_id = self.algod.send_transaction(signed_txn)
        return self.wait_for_transaction(tx_id)

    def get_approval_program(self):
        raise NotImplementedError()

    def get_clear_state_program(self):
        return Approve()
