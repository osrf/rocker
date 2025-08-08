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
import unittest
import pytest

from rocker.constraint_extensions import ShmSize, CpuLimits, MemoryLimits, validate_memory_format
from rocker.core import list_plugins


class ShmSizeExtensionTest(unittest.TestCase):

    def test_shm_size_extension(self):
        plugins = list_plugins()
        shm_size_plugin = plugins['shm_size']
        self.assertEqual(shm_size_plugin.get_name(), 'shm_size')

        p = shm_size_plugin()
        
        # Test docker args
        mock_cliargs = {'shm_size': '512m'}
        args = p.get_docker_args(mock_cliargs)
        self.assertIn('--shm-size 512m', args)
        
        # Test build args  
        mock_cliargs = {'shm_size_build': '1g'}
        build_args = p.get_build_args(mock_cliargs)
        self.assertEqual(build_args, {'shm_size': '1g'})
        
        # Test activation check
        self.assertTrue(p.check_args_for_activation({'shm_size': '512m'}))
        self.assertTrue(p.check_args_for_activation({'shm_size_build': '1g'}))
        self.assertFalse(p.check_args_for_activation({}))

    def test_shm_size_register_arguments(self):
        parser = argparse.ArgumentParser()
        ShmSize.register_arguments(parser)
        
        # Test that both arguments were added
        args = parser.parse_args(['--shm-size', '512m', '--shm-size-build', '1g'])
        self.assertEqual(args.shm_size, '512m')  
        self.assertEqual(args.shm_size_build, '1g')


class CpuLimitsExtensionTest(unittest.TestCase):

    def test_cpu_limits_extension(self):
        plugins = list_plugins()
        cpu_limits_plugin = plugins['cpu_limits']
        self.assertEqual(cpu_limits_plugin.get_name(), 'cpu_limits')

        p = cpu_limits_plugin()
        
        # Test docker args
        mock_cliargs = {'cpus': '1.5'}
        args = p.get_docker_args(mock_cliargs)
        self.assertIn('--cpus 1.5', args)
        
        # Test activation check
        self.assertTrue(p.check_args_for_activation({'cpus': '1.5'}))
        self.assertFalse(p.check_args_for_activation({}))

    def test_cpu_limits_register_arguments(self):
        parser = argparse.ArgumentParser()
        CpuLimits.register_arguments(parser)
        
        # Test valid CPU value
        args = parser.parse_args(['--cpus', '2.0'])
        self.assertEqual(args.cpus, '2.0')

    def test_cpu_validation(self):
        # Test valid CPU formats
        self.assertEqual(CpuLimits._validate_cpu_format('1'), '1')
        self.assertEqual(CpuLimits._validate_cpu_format('1.5'), '1.5')
        self.assertEqual(CpuLimits._validate_cpu_format('0.5'), '0.5')
        
        # Test invalid CPU formats
        with self.assertRaises(argparse.ArgumentTypeError):
            CpuLimits._validate_cpu_format('invalid')
        with self.assertRaises(argparse.ArgumentTypeError):
            CpuLimits._validate_cpu_format('1.5.2')


class MemoryLimitsExtensionTest(unittest.TestCase):

    def test_memory_limits_extension(self):
        plugins = list_plugins()
        memory_limits_plugin = plugins['memory_limits']
        self.assertEqual(memory_limits_plugin.get_name(), 'memory_limits')

        p = memory_limits_plugin()
        
        # Test docker args
        mock_cliargs = {'memory': '2g'}
        args = p.get_docker_args(mock_cliargs)
        self.assertIn('--memory 2g', args)
        
        # Test activation check
        self.assertTrue(p.check_args_for_activation({'memory': '2g'}))
        self.assertFalse(p.check_args_for_activation({}))

    def test_memory_limits_register_arguments(self):
        parser = argparse.ArgumentParser()
        MemoryLimits.register_arguments(parser)
        
        # Test that both short and long form work
        args = parser.parse_args(['--memory', '1g'])
        self.assertEqual(args.memory, '1g')
        
        args = parser.parse_args(['-m', '512m'])
        self.assertEqual(args.memory, '512m')


class ValidateMemoryFormatTest(unittest.TestCase):

    def test_valid_memory_formats(self):
        # Test various valid formats
        valid_formats = [
            '100b', '1024kb', '512mb', '2gb',
            '100k', '512m', '2g',
            '100K', '512M', '2G',
            '1024', # just number should be valid
        ]
        
        for fmt in valid_formats:
            self.assertEqual(validate_memory_format(fmt), fmt)

    def test_invalid_memory_formats(self):
        # Test various invalid formats
        invalid_formats = [
            'invalid',
            '1.5g',  # decimal not supported
            '100tb', # tb not supported
            'g100',  # unit before number
            '',      # empty string
            '100gg', # double unit
        ]
        
        for fmt in invalid_formats:
            with self.assertRaises(argparse.ArgumentTypeError):
                validate_memory_format(fmt)


if __name__ == '__main__':
    unittest.main()