import os
import json
import logging


logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = 'protocol.json'
DEFAULT_CONFIG = {
    'algod_address': 'http://localhost:4001',
    'algod_token': 'a' * 64,
    'kmd_address': 'http://localhost:4002',
    'kmd_token': 'a' * 64,
    'wallet_name': 'unencrypted-default-wallet',
    'wallet_password': '',
    'signing_address': 'a' * 58,
    'teal_version': 4,
    'num_global_byte_slices': 0,
    'num_global_ints': 0,
    'num_local_byte_slices': 0,
    'num_local_ints': 0,
    'app_id': 0
}

config = None


def init_config(**kwargs):
    config = {}
    config.update(DEFAULT_CONFIG)
    config.update({k: v for k, v in kwargs.items() if v})

    save_config(config)


def load_config():
    assert os.path.exists(CONFIG_FILE_NAME), 'Config file not found'

    global config

    if not config:

        with open(CONFIG_FILE_NAME) as conf_file:
            config = json.load(conf_file)

    return config


def save_config(config):
    with open(CONFIG_FILE_NAME, 'w') as conf_file:
        json.dump(config, conf_file, indent=2)
