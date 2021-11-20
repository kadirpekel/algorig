import sys
import importlib
import logging

from komandr import command, main  # noqa

from algorig.config import init_config, DEFAULT_APP_MODULE

logger = logging.getLogger(__name__)


def setup():
    sys.path.append('.')
    try:
        protocol = importlib.import_module(DEFAULT_APP_MODULE)
    except ImportError:
        return

    Application = getattr(protocol, 'Application', None)

    if not Application:
        raise ValueError('`Application` class not implemented')

    app = Application()
    for attr_name in dir(app):
        attr = getattr(app, attr_name)
        if attr_name.startswith('op_') and callable(attr):
            command(name=attr_name[3:])(attr)


@command
def init(algod_address=None,
         algod_token=None,
         kmd_address=None,
         kmd_token=None,
         wallet_name=None,
         wallet_password=None,
         app_module=None,
         signing_address=None,
         teal_version=None,
         section=None,
         num_global_ints=None,
         num_global_byte_slices=None,
         num_local_ints=None,
         num_local_byte_slices=None):
    init_config(algod_address=algod_address,
                algod_token=algod_token,
                kmd_address=kmd_address,
                kmd_token=kmd_token,
                wallet_name=wallet_name,
                wallet_password=wallet_password,
                app_module=app_module,
                signing_address=signing_address,
                teal_version=teal_version,
                section=section,
                num_global_ints=num_global_ints,
                num_global_byte_slices=num_global_byte_slices,
                num_local_ints=num_local_ints,
                num_local_byte_slices=num_local_byte_slices)


setup()
