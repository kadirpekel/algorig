from pyteal import *

from algosdk.future import transaction
from algorig.application import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):
        def on_call():
            return Txn.application_args[0] == Bytes('Hello World')

        return Cond(
            [Txn.application_id() == Int(0), Int(1)],
            [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
            [Txn.on_completion() == OnComplete.NoOp, on_call()],
        )
      
    def op_hello_world(self, my_param):
        self.submit(transaction.ApplicationCallTxn(
            sp=self.algod.suggested_params(),
            on_complete=transaction.OnComplete.NoOpOC,
            index=self.config.getint('app_id'),
            sender=self.config['signing_address'],
            app_args=[my_param)],
        ))
