import sys
import time
import base64
import logging
import importlib
import json

from pyteal import compileTeal, Mode, Approve

from algosdk.v2client import algod
from algosdk import kmd
from algosdk.logic import get_application_address
from algosdk.future.transaction import (assign_group_id,
                                        ApplicationCallTxn,
                                        OnComplete,
                                        StateSchema)


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

    def decode_state(self, state_array):
        state = {}
        for pair in state_array:
            key = base64.b64decode(pair["key"]).decode()
            value = pair["value"]
            valueType = value["type"]
            if valueType == 2:
                # value is uint64
                value = value.get("uint", 0)
            elif valueType == 1:
                # value is byte array
                value = base64.b64decode(value.get("bytes", "")).decode()
            else:
                raise Exception(f"Unexpected state type: {valueType}")
            state[key] = value
        return state

    def fetch_app_info(self):
        return self.algod.application_info(self.config['app_id'])

    def op_dump_state(self, scope):
        '''Dump application state in json format'
        Args:
            scope (enum): Should be either `global` or `local`
        '''
        state = self.decode_app_states(scope)
        self.dump_state(state)

    def dump_state(self, state):
        print(json.dumps(state, indent=2))

    def decode_app_states(self, scope):
        assert scope in ['global', 'local'], \
            'scope should be either `global` or `local`'
        app_info = self.fetch_app_info()
        state = app_info["params"].get(f'{scope}-state', {})
        return self.decode_state(state)

    def wait_for_transaction(self, tx_id, timeout=None):
        timeout = timeout or self.DEFAULT_WAIT_TIMEOUT
        start = last_check = time.time()
        print(f'Processing transaction: {tx_id}')
        while last_check - start < timeout:
            pending_txn = self.algod.pending_transaction_info(tx_id)
            logger.debug(pending_txn)
            print('.', end='', flush=True)
            round = pending_txn.get("confirmed-round", 0)
            if round > 0:
                print()
                print(f'Confirmed at round: {round}')
                return pending_txn
            elif pending_txn["pool-error"]:
                raise Exception(pending_txn["pool-error"])
            time.sleep(1)
        raise Exception('Pending tx not found in timeout rounds')

    def compile_program(self, program):
        return compileTeal(program,
                           mode=Mode.Application,
                           version=self.config['teal_version'])

    def compile_teal(self, teal):
        meta = self.algod.compile(teal)
        return base64.b64decode(meta['result'])

    def get_wallet_token(self):
        entries = self.kmd.list_wallets()
        wallet_name = self.config['wallet_name']
        for entry in entries:
            if entry['name'] == wallet_name:
                wallet_token = entry['id']
                return wallet_token

        raise ValueError(f'Wallet `{wallet_name}` not found on KMD')

    def sign_transaction(self, txn):
        wallet_password = self.config['wallet_password']
        wallet_token = self.get_wallet_token()
        wallet_handle = self.kmd.init_wallet_handle(wallet_token,
                                                    wallet_password)
        signed_txn = self.kmd.sign_transaction(wallet_handle,
                                               wallet_password,
                                               txn)
        self.kmd.release_wallet_handle(wallet_handle)
        return signed_txn

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
        return self.compile_teal(self.get_approval_program_as_teal())

    def get_clear_state_program_bytecode(self):
        return self.compile_teal(self.get_clear_state_program_as_teal())

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
            global_schema=self.get_global_schema(),
            local_schema=self.get_local_schema(),
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
