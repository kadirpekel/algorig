from pyteal import *  # noqa

from algosdk import encoding
from algosdk.future import transaction

from algorig.app import BaseApplication

from contracts import approval_program


class Application(BaseApplication):

    def get_approval_program(self):
        return approval_program()

    def op_application_create(self, seller: str, nft_id: int, start_time: int,
                              end_time: int, reserve: int,
                              min_bid_increment: int):
        '''Creates a new auction.
        Args:
            seller (str): The address of the seller that currently holds the
                          NFT being auctioned.
            nft_id (int): The ID of the NFT being auctioned.
            start_time (int): A UNIX timestamp representing the start time of
                              the auction. This must be greater than the
                              current UNIX timestamp.
            end_time (int): A UNIX timestamp representing the end time of the
                      auction. This must be greater than startTime.
            reserve (int): The reserve amount of the auction. If the auction
                     ends without a bid that is equal to or greater than this
                     amount, the auction will fail, meaning the bid amount will
                     be refunded to the lead bidder and the NFT will return to
                     the seller.
            min_bid_increment (int): The minimum different required between a
                                     new bid and the current leading bid.

        Returns:
            The ID of the newly created auction app.
        '''
        return super().op_application_create(app_args=[
            encoding.decode_address(seller),
            nft_id.to_bytes(8, "big"),
            start_time.to_bytes(8, "big"),
            end_time.to_bytes(8, "big"),
            reserve.to_bytes(8, "big"),
            min_bid_increment.to_bytes(8, "big"),
        ])

    def op_auction_setup(self, funder: str, nft_holder: str, nft_id: int,
                         nft_amount: int):
        '''Finish setting up an auction.

        This operation funds the app auction escrow account, opts that account
        into the NFT, and sends the NFT to the escrow account, all in one
        atomic transaction group. The auction must not have started yet.

        The escrow account requires a total of 0.203 Algos for funding. See
        the code below for a breakdown of this amount.

        Args:
            funder (str): The account providing the funding for the escrow
                          account.
            nft_holder (str): The account holding the NFT.
            nft_id (int): The NFT ID.
            nft_amount (int): The NFT amount being auctioned. Some NFTs has a
                              total supply of 1, while others are fractional
                              NFTs with a greater total supply, so use a value
                              that makes sense for the NFT being auctioned.
        '''
        funding_amount = (
            # min account balance
            100_000
            # additional min balance to opt into NFT
            + 100_000
            # 3 * min txn fee
            + 3 * 1_000
        )

        fund_app_txn = transaction.PaymentTxn(
            sender=funder,
            receiver=self.config['app_address'],
            amt=funding_amount,
            sp=self.suggested_params,
        )

        setup_txn = transaction.ApplicationCallTxn(
            sender=funder,
            index=self.config['app_id'],
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=[b"setup"],
            foreign_assets=[nft_id],
            sp=self.suggested_params,
        )

        fund_nft_txn = transaction.AssetTransferTxn(
            sender=nft_holder,
            receiver=self.config['app_address'],
            index=nft_id,
            amt=nft_amount,
            sp=self.suggested_params,
        )

        self.submit_group([fund_app_txn, setup_txn, fund_nft_txn])

    def op_place_bid(self, bidder: str, bid_ammount: int):
        '''Place a bid on an active auction.

        Args:
            bidder (str): The account providing the bid.
            bid_ammount (int): The amount of the bid.
        '''
        global_state, _ = self.decode_app_states()

        nft_id = global_state[b"nft_id"]
        bid_account = global_state[b"bid_account"]

        if any(bid_account):
            # if "bid_account" is not the zero address
            prev_bid_leader = encoding.encode_address(bid_account)
        else:
            prev_bid_leader = None

        pay_txn = transaction.PaymentTxn(
            sender=bidder,
            receiver=self.config['app_address'],
            amt=bid_ammount,
            sp=self.suggested_params,
        )

        app_call_txn = transaction.ApplicationCallTxn(
            sender=bidder,
            index=self.config['app_id'],
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=[b"bid"],
            foreign_assets=[nft_id],
            # must include the previous lead bidder here to the app can refund
            # that bidder's payment
            accounts=[prev_bid_leader] if prev_bid_leader is not None else [],
            sp=self.suggested_params,
        )

        return self.submit_group([pay_txn, app_call_txn])

    def op_close_auction(self, closer: str):
        '''Close an auction.
        This action can only happen before an auction has begun, in which case
        it is cancelled, or after an auction has ended.
        If called after the auction has ended and the auction was successful,
        the NFT is transferred to the winning bidder and the auction proceeds
        are transferred to the seller. If the auction was not successful, the
        NFT and all funds are transferred to the seller.
        Args:
            closer (str): The account initiating the close transaction. This
                          must be either the seller or auction creator if you
                          wish to close the auction before it starts.
                          Otherwise, this can be any account.
        '''
        global_state, _ = self.decode_app_states()

        nft_id = global_state[b"nft_id"]
        bid_account = global_state[b"bid_account"]

        accounts = [encoding.encode_address(global_state[b"seller"])]

        if any(bid_account):
            # if "bid_account" is not the zero address
            accounts.append(encoding.encode_address(bid_account))

        delete_txn = transaction.ApplicationDeleteTxn(
            sender=closer,
            index=self.config['app_id'],
            accounts=accounts,
            foreign_assets=[nft_id],
            sp=self.suggested_params,
        )
        self.submit(delete_txn)
