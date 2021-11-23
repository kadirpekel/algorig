import sys
import time
import base64
import logging
import importlib

from pyteal import compileTeal, Mode, Int

from algosdk.v2client import algod
from algosdk import kmd
from algosdk.future.transaction import assign_group_id
from algosdk.future.transaction import (ApplicationCreateTxn,
                                        ApplicationUpdateTxn,
                                        OnComplete,
                                        StateSchema)


from algorig.config import load_config, save_config


logger = logging.getLogger(__name__)

APP_MODULE_NAME = 'protocol'
APP_FILE_NAME = f'{APP_MODULE_NAME}.py'
APP_TEMPLATE = '''from pyteal import *

from algorig.application import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):
        # Implement your contract here using pyteal
        return Int(1)

    def op_example_command(self, example_param: int):
        # This is an example method which can be used as cli command
        print(example_param)
'''


def init_application_stub():
    with open(APP_FILE_NAME, 'w') as f:
        f.write(APP_TEMPLATE)


class BaseApplication:

    DEFAULT_WAIT_TIMEOUT = 10

    @classmethod
    def load_from_cwd(cls):
        sys.path.append('.')
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
        wallet_token = self.get_wallet_token()
        wallet_handle = self.kmd.init_wallet_handle(
            wallet_token, self.config['wallet_password'])
        signed_txn = self.kmd.sign_transaction(
            wallet_handle, self.config['wallet_password'], txn)
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

    def build_application_create_txn(self, app_args=None):
        return ApplicationCreateTxn(
            sp=self.algod.suggested_params(),
            sender=self.config['signing_address'],
            on_complete=OnComplete.NoOpOC,
            approval_program=self.get_approval_program_bytecode(),
            clear_program=self.get_clear_state_program_bytecode(),
            global_schema=self.get_global_schema(),
            local_schema=self.get_local_schema(),
            app_args=app_args or [],
        )

    def build_application_update_txn(self, app_args=None):

        app_id = self.config.get('app_id', None)
        if not app_id:
            raise AssertionError('Application not created yet')

        return ApplicationUpdateTxn(
            sp=self.algod.suggested_params(),
            index=app_id,
            sender=self.config['signing_address'],
            approval_program=self.get_approval_program_bytecode(),
            clear_program=self.get_clear_state_program_bytecode(),
            app_args=app_args or [],
        )

    def op_application_create(self, app_args=None, force_creation=False):

        if not force_creation:
            app_id = self.config.get('app_id', None)
            if app_id:
                raise AssertionError('Application already created, '
                                     'please check your config.')

        txn = self.build_application_create_txn(app_args=app_args)
        response = self.submit(txn)
        app_id = response['application-index']
        self.config['app_id'] = app_id
        save_config(self.config)
        print(f'Application created with id: {app_id}.')
        return response

    def op_application_update(self, app_args=None):
        txn = self.build_application_update_txn(app_args=app_args)
        response = self.submit(txn)
        print('Application updated successfully.')
        return response

    def submit_group(self, transactions):
        assign_group_id(transactions)
        signed_transactions = []
        for txn in transactions:
            if txn.sender == self.config['signing_address']:
                signed_txn = self.sign_transaction(txn)
                signed_transactions.append(signed_txn)

        tx_id = self.algod.send_transactions(signed_transactions)
        return self.wait_for_transaction(tx_id)

    def submit(self, txn):
        if txn.sender == self.config['signing_address']:
            signed_txn = self.sign_transaction(txn)

        tx_id = self.algod.send_transaction(signed_txn)
        return self.wait_for_transaction(tx_id)

    def get_approval_program(self):
        raise NotImplementedError()

    def get_clear_state_program(self):
        return Int(1)
