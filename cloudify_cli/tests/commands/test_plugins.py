import inspect
import os
import shutil
import tempfile

import wagon
from functools import wraps
from mock import MagicMock, PropertyMock, patch, Mock

from .constants import PLUGINS_DIR
from .mocks import MockListResponse
from .test_base import CliCommandTest

from cloudify_rest_client import plugins, plugins_update

from cloudify_cli.constants import DEFAULT_TENANT_NAME
from cloudify_cli.exceptions import (CloudifyCliError,
                                     SuppressedCloudifyCliError)


def mock_wait_for_executions(f=None, value=None):
    if not f:
        return lambda _f: mock_wait_for_executions(_f, value)

    @wraps(f)
    def wrapper(*args, **kwargs):
        with patch('cloudify_cli.execution_events_fetcher.wait_for_execution',
                   MagicMock(return_value=PropertyMock(error=value))):
            return f(*args, **kwargs)

    return wrapper


class PluginsTest(CliCommandTest):

    def setUp(self):
        super(PluginsTest, self).setUp()
        self.use_manager()

    def test_plugins_list(self):
        self.client.plugins.list = MagicMock(return_value=MockListResponse())
        self.invoke('cfy plugins list')
        self.invoke('cfy plugins list -t dummy_tenant')
        self.invoke('cfy plugins list -a')

    def test_plugin_get(self):
        self.client.plugins.get = MagicMock(
            return_value=plugins.Plugin({'id': 'id',
                                         'package_name': 'dummy',
                                         'package_version': '1.2',
                                         'supported_platform': 'any',
                                         'distribution_release': 'trusty',
                                         'distribution': 'ubuntu',
                                         'uploaded_at': 'now',
                                         'visibility': 'private',
                                         'created_by': 'admin',
                                         'tenant_name': DEFAULT_TENANT_NAME}))

        self.invoke('cfy plugins get some_id')

    def test_plugins_delete(self):
        self.client.plugins.delete = MagicMock()
        self.invoke('cfy plugins delete a-plugin-id')

    def test_plugins_delete_force(self):
        for flag in ['--force', '-f']:
            mock = MagicMock()
            self.client.plugins.delete = mock
            self.invoke('cfy plugins delete a-plugin-id {0}'.format(
                flag))
            mock.assert_called_once_with(plugin_id='a-plugin-id', force=True)

    def test_plugins_upload(self):
        self.client.plugins.upload = MagicMock()
        plugin_dest_dir = tempfile.mkdtemp()
        try:
            plugin_path = wagon.create(
                'pip',
                archive_destination_dir=plugin_dest_dir
            )
            yaml_path = os.path.join(PLUGINS_DIR, 'plugin.yaml')
            self.invoke('cfy plugins upload {0} -y {1}'.format(plugin_path,
                                                               yaml_path))
        finally:
            shutil.rmtree(plugin_dest_dir, ignore_errors=True)

    def test_plugins_download(self):
        self.client.plugins.download = MagicMock(return_value='some_file')
        self.invoke('cfy plugins download a-plugin-id')

    def test_plugins_set_global(self):
        self.client.plugins.set_global = MagicMock()
        self.invoke('cfy plugins set-global a-plugin-id')

    def test_plugins_set_visibility(self):
        self.client.plugins.set_visibility = MagicMock()
        self.invoke('cfy plugins set-visibility a-plugin-id -l global')

    def test_plugins_set_visibility_invalid_argument(self):
        self.invoke('cfy plugins set-visibility a-plugin-id -l private',
                    err_str_segment='Invalid visibility: `private`',
                    exception=CloudifyCliError)

    def test_plugins_set_visibility_missing_argument(self):
        outcome = self.invoke('cfy plugins set-visibility a-plugin-id',
                              err_str_segment='2',
                              exception=SystemExit)
        self.assertIn('Missing option "-l" / "--visibility"', outcome.output)

    def test_blueprints_set_visibility_wrong_argument(self):
        outcome = self.invoke('cfy plugins set-visibility a-plugin-id -g',
                              err_str_segment='2',
                              exception=SystemExit)
        self.assertIn('Error: no such option: -g', outcome.output)

    def test_plugins_upload_mutually_exclusive_arguments(self):
        outcome = self.invoke(
            'cfy plugins upload --private-resource -l tenant',
            err_str_segment='2',  # Exit code
            exception=SystemExit
        )
        self.assertIn('mutually exclusive with arguments:', outcome.output)

    def test_plugins_upload_invalid_argument(self):
        yaml_path = os.path.join(PLUGINS_DIR, 'plugin.yaml')
        self.invoke('cfy plugins upload {0} -l bla -y {1}'.
                    format(yaml_path, yaml_path),
                    err_str_segment='Invalid visibility: `bla`',
                    exception=CloudifyCliError)

    def test_plugins_upload_with_visibility(self):
        self.client.plugins.upload = MagicMock()
        yaml_path = os.path.join(PLUGINS_DIR, 'plugin.yaml')
        self.invoke('cfy plugins upload {0} -l private -y {1}'
                    .format(yaml_path, yaml_path))

    def test_calls_rest_client_correctly(self):
        pass

    def test_waits_for_execution_to_finish(self):
        pass

    def test_raises_when_execution_fails(self):
        pass


class PluginsUpdateTest(CliCommandTest):

    def setUp(self):
        super(PluginsUpdateTest, self).setUp()
        self.use_manager()

    def test_plugins_get(self):
        self.client.plugins_update.get = MagicMock(
            return_value=plugins_update.PluginsUpdate({
                'id': 'asdf'
            }))
        outcome = self.invoke('cfy plugins get-update asdf')
        self.assertIn('asdf', outcome.output)

    def test_plugins_list(self):
        self.asserTrue(False)

    def test_plugins_update_successful(self):
        outcome = self.invoke('cfy plugins update -b asdf')
        self.assertIn('Updating the plugins of the deployments of the '
                      'blueprint asdf', outcome.logs)
        self.assertIn('Finished executing workflow', outcome.logs)
        self.assertIn('Successfully updated plugins for blueprint asdf.',
                      outcome.logs)

    def test_update_force_flag_is_false(self):
        update_client_mock = Mock()
        self.client.deployment_updates.update_with_existing_blueprint = \
            update_client_mock
        self.invoke('cfy plugins update -b asdf')

        calls = self.client.plugins_update.update_plugins.mock_calls
        self.assertEqual(len(calls), 1)
        _, args, kwargs = calls[0]
        call_args = inspect.getcallargs(
            plugins_update.PluginsUpdateClient(None).update_plugins,
            *args, **kwargs)

        self.assertIn('force', call_args)
        self.assertFalse(call_args['force'])

    def test_update_force_flag_is_true(self):
        update_client_mock = Mock()
        self.client.deployment_updates.update_with_existing_blueprint = \
            update_client_mock
        self.invoke('cfy plugins update -b asdf --force')

        calls = self.client.plugins_update.update_plugins.mock_calls
        self.assertEqual(len(calls), 1)
        _, args, kwargs = calls[0]
        call_args = inspect.getcallargs(
            plugins_update.PluginsUpdateClient(None).update_plugins,
            *args, **kwargs)

        self.assertIn('force', call_args)
        self.assertTrue(call_args['force'])

    @mock_wait_for_executions(value=True)
    def test_deployment_update_failure(self):
        outcome = self.invoke(
            'cfy plugins update -b asdf',
            err_str_segment='',
            exception=SuppressedCloudifyCliError)

        logs = outcome.logs.split('\n')
        self.assertIn('Updating deployment my_deployment', logs[-3])
        self.assertIn('Execution of workflow', logs[-2])
        self.assertIn('failed', logs[-2])
        self.assertIn('Failed updating deployment my_deployment', logs[-1])
