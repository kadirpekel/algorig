# flake8: noqa

from pyteal import *

from algosdk.future import transaction
from algorig.app import BaseApplication


class Application(BaseApplication):

    def get_approval_program(self):

        @Subroutine(TealType.uint64)
        def on_call():
            return Seq([
                    App.localPut(Int(0), Bytes("voted"), Int(1)),
                    Approve(),
            ])

        return Cond(
            [Txn.application_id() == Int(0), Int(1)],
            [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
            [Txn.on_completion() == OnComplete.OptIn, Int(1)],
            [Txn.on_completion() == OnComplete.DeleteApplication, Int(1)],
            [Txn.on_completion() == OnComplete.ClearState, Int(1)],
            [Txn.on_completion() == OnComplete.CloseOut, Int(1)],
            [Txn.on_completion() == OnComplete.NoOp, on_call()],
        )
      
    def op_application_vote(self, voter_address):

        already_opted_in = False
        account_info = self.algod.account_info(voter_address)
        apps_local_state = account_info.get('apps-local-state', [])
        for app_local_state in apps_local_state:
            if app_local_state['id'] == self.config['app_id']:
                print('Already opted in')
                already_opted_in = True
                break

        txns = []

        if not already_opted_in:
            txns.append(transaction.ApplicationOptInTxn(
                sp=self.suggested_params,
                sender=voter_address,
                index=self.config['app_id']
            ))

        txns.append(transaction.ApplicationCallTxn(
            sp=self.suggested_params,
            on_complete=transaction.OnComplete.NoOpOC,
            sender=voter_address,
            index=self.config['app_id'],
            app_args=['vote'],
        ))

        self.submit_group(txns)
