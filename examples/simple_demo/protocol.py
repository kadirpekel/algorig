# flake8: noqa
from pyteal import *

from algosdk import transaction
from algorig.app import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):
        
        def on_call():
            return Return(Txn.application_args[0] == Bytes('Hello World'))

        return Cond(
            [Txn.application_id() == Int(0), Approve()],
            [Txn.on_completion() == OnComplete.UpdateApplication, Approve()],
            [Txn.on_completion() == OnComplete.NoOp, on_call()],
        )
      
    def op_send_greeting(self, greeting):
        self.submit(transaction.ApplicationCallTxn(
            sp=self.suggested_params,
            on_complete=transaction.OnComplete.NoOpOC,
            index=self.config['app_id'],
            sender=self.config['signing_address'],
            app_args=[greeting],
        ))
