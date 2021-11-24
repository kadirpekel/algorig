import pytest

from unittest import mock

from algorig import config


@pytest.fixture
def config_data():
    return '''{
    "foo": "bar",
    "x": 1,
    "y": 2
}
'''


def test_init_config(config_data):
    c = {
        'a': 'foo',
        'b': 2,
        'c': None,
    }
    with mock.patch('algorig.config.DEFAULT_CONFIG', c):
        with mock.patch('algorig.config.save_config') as save_config:
            config.init_config(a=None, b=3, c='bar', d='baz')
            save_config.assert_called_once_with({
                'a': 'foo',
                'b': 3,
                'c': 'bar',
                'd': 'baz'
            })


def test_load_config(config_data):

    with mock.patch('os.path.exists', lambda x: False):
        with pytest.raises(AssertionError):
            c = config.load_config()

    with mock.patch('os.path.exists', lambda x: True):
        with mock.patch('builtins.open',
                        mock.mock_open(read_data=config_data)) as mock_open:
            c = config.load_config()
            c = config.load_config()  # check if global variable caching works
            mock_open.assert_called_once_with(config.CONFIG_FILE_NAME)

            c = config.load_config()
            assert c['foo'] == 'bar'
            assert c['x'] == 1
            assert c['y'] == 2


def test_save_config(config_data):
    with mock.patch('builtins.open') as mock_open:
        with mock.patch('os.path.exists', lambda x: True):
            c = config.load_config()
            config.save_config(c)
            mock_open.assert_called_once_with(config.CONFIG_FILE_NAME, 'w')
