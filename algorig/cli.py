from komandr import command, main  # noqa

from algorig.config import init_config
from algorig.app import init_application_stub, BaseApplication


@command
def init(algod_address=None,
         algod_token=None,
         kmd_address=None,
         kmd_token=None,
         wallet_name=None,
         wallet_password=None,
         signing_address=None,
         teal_version: int = None,
         num_global_ints: int = None,
         num_global_byte_slices: int = None,
         num_local_ints: int = None,
         num_local_byte_slices: int = None):

    init_config(algod_address=algod_address,
                algod_token=algod_token,
                kmd_address=kmd_address,
                kmd_token=kmd_token,
                wallet_name=wallet_name,
                wallet_password=wallet_password,
                signing_address=signing_address,
                teal_version=teal_version,
                num_global_ints=num_global_ints,
                num_global_byte_slices=num_global_byte_slices,
                num_local_ints=num_local_ints,
                num_local_byte_slices=num_local_byte_slices)

    init_application_stub()

    print('Algorig inited.')


try:
    application = BaseApplication.load_from_cwd()
    application.generate_commands()
except ImportError:
    pass
