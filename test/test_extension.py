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
import pwd
from io import BytesIO as StringIO


from rocker.core import DockerImageGenerator
from rocker.core import docker_build
from rocker.core import list_plugins
from rocker.extensions import name_to_argument


def plugin_load_parser_correctly(plugin):
    """A helper function to test that the plugins at least
    register an option for their own name."""
    parser = argparse.ArgumentParser(description='test_parser')
    plugin.register_arguments(parser)
    argument_name = name_to_argument(plugin.get_name())
    for action in parser._actions:
        option_strings = getattr(action, 'option_strings', [])
        if argument_name in option_strings:
            return True
    return False


class ExtensionsTest(unittest.TestCase):
    def test_name_to_argument(self):
        self.assertEqual(name_to_argument('asdf'), '--asdf')
        self.assertEqual(name_to_argument('as_df'), '--as-df')
        self.assertEqual(name_to_argument('as-df'), '--as-df')


class DevicesExtensionTest(unittest.TestCase):

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

    def test_devices_extension(self):
        plugins = list_plugins()
        devices_plugin = plugins['devices']
        self.assertEqual(devices_plugin.get_name(), 'devices')

        p = devices_plugin()
        self.assertTrue(plugin_load_parser_correctly(devices_plugin))
        
        mock_cliargs = {'devices': ['/dev/random']}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--device /dev/random' in args)

        # Check case for invalid device
        mock_cliargs = {'devices': ['/dev/does_not_exist']}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertFalse('--device' in args)


class HomeExtensionTest(unittest.TestCase):

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

    def test_home_extension(self):
        plugins = list_plugins()
        home_plugin = plugins['home']
        self.assertEqual(home_plugin.get_name(), 'home')

        p = home_plugin()
        self.assertTrue(plugin_load_parser_correctly(home_plugin))
        
        mock_cliargs = {}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('-v %s:%s' % (Path.home(), Path.home()) in args)

class NetworkExtensionTest(unittest.TestCase):

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

    def test_network_extension(self):
        plugins = list_plugins()
        network_plugin = plugins['network']
        self.assertEqual(network_plugin.get_name(), 'network')

        p = network_plugin()
        self.assertTrue(plugin_load_parser_correctly(network_plugin))
        
        mock_cliargs = {'network': 'none'}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--network none' in args)

        mock_cliargs = {'network': 'host'}
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--network host' in args)


class NameExtensionTest(unittest.TestCase):

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

    def test_name_extension(self):
        plugins = list_plugins()
        name_plugin = plugins['name']
        self.assertEqual(name_plugin.get_name(), 'name')

        p = name_plugin()
        self.assertTrue(plugin_load_parser_correctly(name_plugin))

        mock_cliargs = {'name': 'none'}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--name none' in args)

        mock_cliargs = {'name': 'docker_name'}
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--name docker_name' in args)


class PrivilegedExtensionTest(unittest.TestCase):

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

    def test_privileged_extension(self):
        plugins = list_plugins()
        print(plugins)
        privileged_plugin = plugins['privileged']
        self.assertEqual(privileged_plugin.get_name(), 'privileged')

        p = privileged_plugin()
        self.assertTrue(plugin_load_parser_correctly(privileged_plugin))

        mock_cliargs = {'privileged': True}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('--privileged' in args)


class UserExtensionTest(unittest.TestCase):

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

    def test_user_extension(self):
        plugins = list_plugins()
        user_plugin = plugins['user']
        self.assertEqual(user_plugin.get_name(), 'user')

        p = user_plugin()
        self.assertTrue(plugin_load_parser_correctly(user_plugin))

        env_subs = p.get_environment_subs()
        self.assertEqual(env_subs['gid'], os.getgid())
        self.assertEqual(env_subs['uid'], os.getuid())
        self.assertEqual(env_subs['name'],  getpass.getuser())
        self.assertEqual(env_subs['dir'],  str(Path.home()))
        self.assertEqual(env_subs['gecos'],  pwd.getpwuid(os.getuid()).pw_gecos)
        self.assertEqual(env_subs['shell'],  pwd.getpwuid(os.getuid()).pw_shell)

        mock_cliargs = {}
        snippet = p.get_snippet(mock_cliargs).splitlines()

        uid_line = [l for l in snippet if '--uid' in l][0]
        self.assertTrue(str(os.getuid()) in uid_line)

        self.assertEqual(p.get_preamble(mock_cliargs), '')
        self.assertEqual(p.get_docker_args(mock_cliargs), '')

        self.assertTrue('mkhomedir_helper' in p.get_snippet(mock_cliargs))
        home_active_cliargs = mock_cliargs
        home_active_cliargs['home'] = True
        self.assertFalse('mkhomedir_helper' in p.get_snippet(home_active_cliargs))

        user_override_active_cliargs = mock_cliargs
        user_override_active_cliargs['user_override_name'] = 'testusername'
        snippet_result = p.get_snippet(user_override_active_cliargs)
        self.assertTrue('USER testusername' in snippet_result)
        self.assertTrue('WORKDIR /home/testusername' in snippet_result)
        self.assertTrue('userdel -r' in snippet_result)

        user_override_active_cliargs['user_preserve_home'] = True
        snippet_result = p.get_snippet(user_override_active_cliargs)
        self.assertFalse('userdel -r' in snippet_result)

    def test_user_collisions(self):
        plugins = list_plugins()
        user_plugin = plugins['user']
        self.assertEqual(user_plugin.get_name(), 'user')

        uid = os.getuid()+1
        COLLIDING_UID_DOCKERFILE = f"""FROM ubuntu:jammy
RUN useradd test -u{uid}

"""
        iof = StringIO(COLLIDING_UID_DOCKERFILE.encode())
        image_id = docker_build(
            fileobj=iof,
            #output_callback=output_callback,
            nocache=True,
            forcerm=True,
            tag="rocker:" + f"user_extension_test_uid_collision"
        )
        print(f'Image id is {image_id}')
        self.assertTrue(image_id, f"Image failed to build >>>{COLLIDING_UID_DOCKERFILE}<<<")

        # Test Colliding UID but not name
        build_args = {
            'user': True,
            'user_override_name': 'test2',
            'user_preserve_home': True,
            # 'command': 'ls -l && touch /home/test2/home_directory_access_verification',
            'command': 'touch /home/test2/testwrite',
        } 
        dig = DockerImageGenerator([user_plugin()], build_args, image_id)
        exit_code = dig.build(**build_args)
        self.assertTrue(exit_code == 0, f"Build failed with exit code {exit_code}")
        run_exit_code = dig.run(**build_args)
        self.assertTrue(run_exit_code == 0, f"Run failed with exit code {run_exit_code}")


        # Test colliding UID and name
        build_args['user_override_name'] = 'test'
        build_args['command'] = 'touch /home/test/testwrite'
        dig = DockerImageGenerator([user_plugin()], build_args, image_id)
        exit_code = dig.build(**build_args)
        self.assertTrue(exit_code == 0, f"Build failed with exit code {exit_code}")
        run_exit_code = dig.run(**build_args)
        self.assertTrue(run_exit_code == 0, f"Run failed with exit code {run_exit_code}")


class PulseExtensionTest(unittest.TestCase):

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

    def test_pulse_extension(self):
        plugins = list_plugins()
        pulse_plugin = plugins['pulse']
        self.assertEqual(pulse_plugin.get_name(), 'pulse')

        p = pulse_plugin()
        self.assertTrue(plugin_load_parser_correctly(pulse_plugin))
        
        mock_cliargs = {}
        snippet = p.get_snippet(mock_cliargs)
        #first line
        self.assertIn('RUN mkdir -p /etc/pulse', snippet)
        self.assertIn('default-server = unix:/run/user/', snippet) #skipping user id that's system dependent
        self.assertIn('autospawn = no', snippet)
        self.assertIn('daemon-binary = /bin/true', snippet)
        #last line
        self.assertIn('> /etc/pulse/client.conf', snippet)
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        docker_args = p.get_docker_args(mock_cliargs)
        self.assertIn('-v /run/user/', docker_args)
        self.assertIn('/pulse:/run/user/', docker_args)
        self.assertIn('/pulse --device /dev/snd ', docker_args)
        self.assertIn(' -e PULSE_SERVER=unix', docker_args)
        self.assertIn('/pulse/native -v', docker_args)
        self.assertIn('/pulse/native:', docker_args)
        self.assertIn('/pulse/native --group-add', docker_args)

EXPECTED_DEV_HELPERS_SNIPPET = """# workspace development helpers
RUN apt-get update \\
 && apt-get install -y \\
    byobu \\
    emacs \\
 && apt-get clean
"""

class DevHelpersExtensionTest(unittest.TestCase):

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

    def test_pulse_extension(self):
        plugins = list_plugins()
        dev_helper_plugin = plugins['dev_helpers']
        self.assertEqual(dev_helper_plugin.get_name(), 'dev_helpers')

        p = dev_helper_plugin()
        self.assertTrue(plugin_load_parser_correctly(dev_helper_plugin))
        
        mock_cliargs = {}

        self.assertEqual(p.get_snippet(mock_cliargs), EXPECTED_DEV_HELPERS_SNIPPET)
        self.assertEqual(p.get_preamble(mock_cliargs), '')


class EnvExtensionTest(unittest.TestCase):

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

    def test_env_extension(self):
        plugins = list_plugins()
        env_plugin = plugins['env']
        self.assertEqual(env_plugin.get_name(), 'env')

        p = env_plugin()
        self.assertTrue(plugin_load_parser_correctly(env_plugin))
        
        mock_cliargs = {'env': [['ENVVARNAME=envvar_value', 'ENV2=val2'], ['ENV3=val3']]}

        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        self.assertEqual(p.get_docker_args(mock_cliargs), ' -e ENVVARNAME=envvar_value -e ENV2=val2 -e ENV3=val3')

    def test_env_file_extension(self):
        plugins = list_plugins()
        env_plugin = plugins['env']
        self.assertEqual(env_plugin.get_name(), 'env')

        p = env_plugin()
        self.assertTrue(plugin_load_parser_correctly(env_plugin))
        
        mock_cliargs = {'env_file': [['foo'], ['bar']]}

        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        self.assertEqual(p.get_docker_args(mock_cliargs), ' --env-file foo --env-file bar')
