########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############

__author__ = 'ran'

from cosmo_cli.cosmo_cli import BaseProviderClass


class ProviderManager(BaseProviderClass):

    # def __init__(self, provider_config=None, is_verbose_output=False):
    #     self.provider_config = provider_config
    #     self.is_verbose_output = is_verbose_output
    #     # self.schema = PROVIDER_SCHEMA

    def provision(self):
        return '10.0.0.2', '10.10.10.10', 'key_path', 'user', {'key': 'value'}

    def bootstrap(self, mgmt_ip, private_ip, mgmt_ssh_key, mgmt_ssh_user,
                  dev_mode=False):
        return True

    def validate(self, validation_errors={}):
        # get openstack clients
        return validation_errors

    def teardown(self, provider_context, ignore_validation=False):
        raise RuntimeError('cloudify_mock_provider2 teardown exception')
