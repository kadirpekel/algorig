from pyteal import *

from algosdk.future import transaction
from algorig.app import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):
        def on_call():
            return Txn.application_args[0] == Bytes('setup')

        return Cond(
            [Txn.application_id() == Int(0), Int(1)],
            [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
            [Txn.on_completion() == OnComplete.NoOp, on_call()],
        )
      
    def op_application_setup(self, funder_address):

        fund_app_txn = transaction.PaymentTxn(
            sp=self.suggested_params,
            sender=funder_address,
            receiver=self.config['app_address'],
            amt=1_000
        )

        setup_app_txn = transaction.ApplicationCallTxn(
            sp=self.suggested_params,
            on_complete=transaction.OnComplete.NoOpOC,
            sender=self.config['signing_address'],
            index=self.config['app_id'],
            app_args=['setup'],
        )

        self.submit_group([
            fund_app_txn,
            setup_app_txn,
        ])
