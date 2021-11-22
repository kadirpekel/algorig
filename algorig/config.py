import logging
import configparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_SECTION = 'DEFAULT'
CONFIG_FILE_NAME = '.rig.rc'


DEFAULT_APP_MODULE = 'protocol'
DEFAULT_APP_ID = 1
DEFAULT_APP_FILE_NAME = f'{DEFAULT_APP_MODULE}.py'

DEFAULT_TEAL_VERSION = 4
DEFAULT_SIGNING_ADDRESS = 'a' * 58
DEFAULT_ALGOD_ADDRESS = 'http://localhost:4001'
DEFAULT_KMD_ADDRESS = 'http://localhost:4002'
DEFAULT_ALGOD_TOKEN = DEFAULT_KMD_TOKEN = 'a' * 64
DEFAULT_WALLET_NAME = 'unencrypted-default-wallet'
DEFAULT_WALLET_PASSWORD = ''

config = None

app_template = '''
from pyteal import *

from algorig.application import BaseApplication

class Application(BaseApplication):

    def get_approval_program(self):
        # Implement your contract here using pyteal
        return Int(0)

    def op_example_command(self, example_param: int):
        # This is an example method which can be used as cli command
        print(example_param)

'''


def init_config(algod_address=None,
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
                num_local_byte_slices=None,
                app_id=None):

    section = section or DEFAULT_CONFIG_SECTION

    config = configparser.ConfigParser()

    config[section] = {
        'algod_address': algod_address or DEFAULT_ALGOD_ADDRESS,
        'algod_token': algod_token or DEFAULT_ALGOD_TOKEN,
        'kmd_address': kmd_address or DEFAULT_KMD_ADDRESS,
        'kmd_token': kmd_token or DEFAULT_KMD_TOKEN,
        'wallet_name': wallet_name or DEFAULT_WALLET_NAME,
        'wallet_password': wallet_password or DEFAULT_WALLET_PASSWORD,
        'signing_address': signing_address or DEFAULT_SIGNING_ADDRESS,
        'app_module': app_module or DEFAULT_APP_MODULE,
        'teal_version': teal_version or DEFAULT_TEAL_VERSION,
        'num_global_byte_slices': num_global_byte_slices or 0,
        'num_global_ints': num_global_byte_slices or 0,
        'num_local_byte_slices': num_local_byte_slices or 0,
        'num_local_ints': num_local_byte_slices or 0,
        'app_id': app_id or DEFAULT_APP_ID
    }

    save_config(config)

    if not app_module:
        with open(DEFAULT_APP_FILE_NAME, 'w') as app_file:
            app_file.write(app_template)

    logger.info(f'Algorig inited with config file: "{CONFIG_FILE_NAME}"')

    return config


def load_config():
    global config

    if not config:

        config = configparser.ConfigParser()

        try:
            with open(CONFIG_FILE_NAME) as conf_file:
                config.read_file(conf_file)
        except FileNotFoundError:
            logger.error('You need to init and configure algorig first')

    return config


def save_config(config_instance=None):
    global config
    new_config = config_instance or config
    with open(CONFIG_FILE_NAME, 'w') as conf_file:
        new_config.write(conf_file)


def get_config_section(section=None):
    config = load_config()
    return config[section or DEFAULT_CONFIG_SECTION]
