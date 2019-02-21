import json

from ..cli import cfy
from ..table import print_data

CONFIG_COLUMNS = ['name', 'value', 'updated_at']


@cfy.group(name='admin')
@cfy.options.common_options
@cfy.assert_manager_active()
def admin():
    pass


@admin.group(name='config')
def config():
    pass


@config.command(name='get')
@cfy.pass_client()
@cfy.pass_logger
def config_get(client, logger):
    config = client.manager.get_config()
    print_data(CONFIG_COLUMNS, config, 'Manager config:')


@config.command(name='set')
@cfy.pass_client()
@cfy.argument('option-name')
@cfy.argument('option-value')
@cfy.options.inputs
@cfy.pass_logger
def config_update(client, logger, option_name, option_value):
    client.manager.put_config(option_name, json.loads(option_value))
