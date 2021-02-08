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
import unittest

from itertools import chain

from rocker.core import DockerImageGenerator
from rocker.core import list_plugins
from rocker.core import get_docker_client
from rocker.core import get_rocker_version
from rocker.core import RockerExtensionManager

class RockerCoreTest(unittest.TestCase):

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

    def test_list_plugins(self):
        plugins_found = list_plugins()
        plugin_names = plugins_found.keys()
        self.assertTrue('nvidia' in plugin_names )
        self.assertTrue('pulse' in plugin_names )
        self.assertTrue('user' in plugin_names )
        self.assertTrue('home' in plugin_names )

    def test_get_rocker_version(self):
        v = get_rocker_version()
        parts = v.split('.')
        self.assertEqual(len(parts), 3)
        for p in parts:
            # Check that it can be cast to an int
            i = int(p)

    def test_run_before_build(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.run('true'), 1)
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)

    def test_return_code_no_extensions(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)
        self.assertEqual(dig.run('false'), 1)

    def test_return_code_multiple_extensions(self):
        plugins = list_plugins()
        desired_plugins = ['home', 'user']
        active_extensions = [e() for e in plugins.values() if e.get_name() in desired_plugins]
        dig = DockerImageGenerator(active_extensions, {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true'), 0)
        self.assertEqual(dig.run('false'), 1)

    def test_noexecute(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true', noexecute=True), 0)

    def test_dry_run(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true', mode='dry-run'), 0)
        self.assertEqual(dig.run('false', mode='dry-run'), 0)

    def test_non_interactive(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true', mode='non-interactive'), 0)
        self.assertEqual(dig.run('false', mode='non-interactive'), 1)

    def test_device(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        self.assertEqual(dig.run('true', devices=['/dev/random']), 0)
        self.assertEqual(dig.run('true', devices=['/dev/does_not_exist']), 0)

    def test_network(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')
        self.assertEqual(dig.build(), 0)
        networks = ['bridge', 'host', 'none']
        for n in networks:
            self.assertEqual(dig.run('true', network=n), 0)

    def test_extension_manager(self):
        parser = argparse.ArgumentParser()
        extension_manager = RockerExtensionManager()
        default_args = {}
        extension_manager.extend_cli_parser(parser, default_args)
        help_str = parser.format_help()
        self.assertIn('--mode', help_str)
        self.assertIn('dry-run', help_str)
        self.assertIn('non-interactive', help_str)
        self.assertIn('--extension-blacklist', help_str)

        active_extensions = active_extensions = extension_manager.get_active_extensions({'user': True, 'ssh': True, 'extension_blacklist': ['ssh']})
        self.assertEqual(len(active_extensions), 1)
        self.assertEqual(active_extensions[0].get_name(), 'user')

    def test_docker_cmd_interactive(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')

        self.assertNotIn('-it', dig.generate_docker_cmd(mode=''))
        self.assertIn('-it', dig.generate_docker_cmd(mode='dry-run'))

        # TODO(tfoote) mock this appropriately
        # google actions tests don't have a tty, local tests do
        import os, sys
        if os.isatty(sys.__stdin__.fileno()):
            self.assertIn('-it', dig.generate_docker_cmd(mode='interactive'))
        else:
            self.assertNotIn('-it', dig.generate_docker_cmd(mode='interactive'))

        self.assertNotIn('-it', dig.generate_docker_cmd(mode='non-interactive'))


    def test_docker_cmd_nocleanup(self):
        dig = DockerImageGenerator([], {}, 'ubuntu:bionic')

        self.assertIn('--rm', dig.generate_docker_cmd())
        self.assertIn('--rm', dig.generate_docker_cmd(mode='dry-run'))
        self.assertIn('--rm', dig.generate_docker_cmd(nocleanup=''))

        self.assertNotIn('--rm', dig.generate_docker_cmd(nocleanup='true'))