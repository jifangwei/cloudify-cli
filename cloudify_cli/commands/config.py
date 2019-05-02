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
