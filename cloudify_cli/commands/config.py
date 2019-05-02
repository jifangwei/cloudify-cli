from ..cli import cfy
from ..table import print_data

CONFIG_COLUMNS = [
    'name', 'value', 'scope', 'updated_at'
]


@cfy.group(name='config')
def config():
    pass


@config.command(name='list')
@cfy.pass_client()
def list_config(client):
    configs = client.manager.get_config()
    print_data(CONFIG_COLUMNS, configs, 'Config:')


@config.command(name='update')
@cfy.pass_client()
@cfy.pass_logger
@cfy.argument('name')
@cfy.argument('value')
def update_config(client, name, value, logger):
    client.manager.put_config(name, value)
    logger.info('Set %s to %s', name, value)
