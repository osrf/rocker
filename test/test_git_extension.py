# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import argparse
import em
import getpass
import os
import unittest
from pathlib import Path
from unittest import mock
import pwd
import tempfile


from rocker.core import list_plugins
from rocker.extensions import name_to_argument
from rocker.git_extension import Git

from test_extension import plugin_load_parser_correctly

class ExtensionsTest(unittest.TestCase):
    def test_name_to_argument(self):
        self.assertEqual(name_to_argument('asdf'), '--asdf')
        self.assertEqual(name_to_argument('as_df'), '--as-df')
        self.assertEqual(name_to_argument('as-df'), '--as-df')


class GitExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_git_extension(self):
        plugins = list_plugins()
        git_plugin = plugins['git']
        self.assertEqual(git_plugin.get_name(), 'git')

        p = git_plugin()
        self.assertTrue(plugin_load_parser_correctly(git_plugin))


        mock_cliargs = {}
        mock_config_file = tempfile.NamedTemporaryFile()
        mock_system_config_file = tempfile.NamedTemporaryFile()
        mock_cliargs['git_config_path'] = mock_config_file.name
        mock_cliargs['git_config_path_system'] = mock_system_config_file.name
        args = p.get_docker_args(mock_cliargs)
        system_gitconfig = mock_system_config_file.name
        system_gitconfig_target = '/etc/gitconfig'
        user_gitconfig = mock_config_file.name
        user_gitconfig_target = '/root/.gitconfig'
        self.assertIn('-v %s:%s' % (system_gitconfig, system_gitconfig_target), args)
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), args)

        # Test with user "enabled"
        mock_cliargs = {'user': True}
        mock_cliargs['git_config_path'] = mock_config_file.name
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = os.path.expanduser('~/.gitconfig')
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test with an existing overridden user key, but with None value
        mock_cliargs['user_override_name'] = None
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = os.path.expanduser('~/.gitconfig')
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test with overridden user
        mock_cliargs['user_override_name'] = 'testusername'
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = '/home/testusername/.gitconfig'
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test with overridden home directory
        mock_cliargs['user_override_home'] = '/home/otherdir'
        user_args = p.get_docker_args(mock_cliargs)
        user_gitconfig_target = '/home/otherdir/.gitconfig'
        self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), user_args)

        # Test non-extant files no generation
        mock_cliargs['git_config_path'] = '/path-does-not-exist'
        mock_cliargs['git_config_path_system'] = '/path-does-not-exist-either'
        user_args = p.get_docker_args(mock_cliargs)
        self.assertNotIn('-v', user_args)

    def _user_gitconfig_args(self, pw_dir, **overrides):
        passwd = pwd.struct_passwd(('someuser', 'x', 1000, 1000, '', pw_dir, '/bin/bash'))
        mock_config_file = tempfile.NamedTemporaryFile()
        mock_cliargs = {'user': True, 'git_config_path': mock_config_file.name,
                        'git_config_path_system': '/path-does-not-exist'}
        mock_cliargs.update(overrides)
        with mock.patch('rocker.extensions.pwd.getpwuid', return_value=passwd):
            return mock_config_file.name, Git().get_docker_args(mock_cliargs)

    def test_git_extension_user_home_is_root(self):
        # The user extension creates the user with the home of the host user,
        # which is /root when running as root.
        user_gitconfig, args = self._user_gitconfig_args('/root')
        self.assertIn('-v %s:/root/.gitconfig' % user_gitconfig, args)
        self.assertNotIn('/home/', args)

    def test_git_extension_user_home_outside_home(self):
        user_gitconfig, args = self._user_gitconfig_args('/srv/someuser')
        self.assertIn('-v %s:/srv/someuser/.gitconfig' % user_gitconfig, args)

    def test_git_extension_override_home_takes_precedence(self):
        user_gitconfig, args = self._user_gitconfig_args('/root', user_override_home='/data/other')
        self.assertIn('-v %s:/data/other/.gitconfig' % user_gitconfig, args)
        user_gitconfig, args = self._user_gitconfig_args(
            '/root', user_override_name='other', user_override_home='/data/other')
        self.assertIn('-v %s:/data/other/.gitconfig' % user_gitconfig, args)

    def test_git_extension_override_name_with_root_home(self):
        user_gitconfig, args = self._user_gitconfig_args('/root', user_override_name='other')
        self.assertIn('-v %s:/home/other/.gitconfig' % user_gitconfig, args)
