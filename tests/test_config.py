import pytest
from unittest import mock

from algorig.config import load_config, CONFIG_FILE_NAME


@pytest.fixture
def config_data():
    return '''[FIRST_SECTION]
first_key = first_value
second_key = second_value
[SECOND_SECTION]
third_key = third_value
'''


def test_load_config(config_data):

    with mock.patch('os.path.exists', lambda x: False) as path_exists:
        with pytest.raises(AssertionError):
            config = load_config()

    with mock.patch('os.path.exists', lambda x: True):
        with mock.patch('builtins.open',
                    mock.mock_open(read_data=config_data)) as mock_open:
            config = load_config()
            config = load_config() # check if global variable caching works
            mock_open.assert_called_once_with(CONFIG_FILE_NAME)

            config = load_config()
            sections = config.sections()
            assert sections == ['FIRST_SECTION', 'SECOND_SECTION']
            first_section = config['FIRST_SECTION']
            assert first_section['first_key'] == 'first_value'
            assert first_section['second_key'] == 'second_value'
            second_section = config['SECOND_SECTION']
            assert second_section['third_key'] == 'third_value'
