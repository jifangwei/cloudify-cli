
from ..cli import cfy


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
    print config
