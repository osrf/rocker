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

import unittest
from argparse import ArgumentTypeError

from rocker.ulimit_extension import Ulimit


class UlimitTest(unittest.TestCase):
    """Unit tests for the Ulimit class."""

    def setUp(self):
        self._instance = Ulimit()

    def _is_arg_translation_ok(self, mock_cliargs, expected):
        is_ok = False
        message_string = ""
        try:
            docker_args = self._instance.get_docker_args(
                {self._instance.get_name(): [mock_cliargs]})
            is_ok = docker_args == expected
            message_string = f"Expected: '{expected}', got: '{docker_args}'"
        except ArgumentTypeError:
            message_string = "Incorrect argument format"
        return (is_ok, message_string)

    def test_args_single_soft(self):
        """Test single soft limit argument."""
        mock_cliargs = ["rtprio=99"]
        expected = " --ulimit rtprio=99"
        self.assertTrue(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_multiple_soft(self):
        """Test multiple soft limit arguments."""
        mock_cliargs = ["rtprio=99", "memlock=102400"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400"
        self.assertTrue(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_single_hard(self):
        """Test single hard limit argument."""
        mock_cliargs = ["nofile=1024:524288"]
        expected = " --ulimit nofile=1024:524288"
        self.assertTrue(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_multiple_hard(self):
        """Test multiple hard limit arguments."""
        mock_cliargs = ["nofile=1024:524288", "rtprio=90:99"]
        expected = " --ulimit nofile=1024:524288 --ulimit rtprio=90:99"
        self.assertTrue(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_multiple_mix(self):
        """Test multiple mixed limit arguments."""
        mock_cliargs = ["rtprio=99", "memlock=102400", "nofile=1024:524288"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400 --ulimit nofile=1024:524288"
        self.assertTrue(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_wrong_single_soft(self):
        """Test if single soft limit argument is wrong."""
        mock_cliargs = ["rtprio99"]
        expected = " --ulimit rtprio99"
        self.assertFalse(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_wrong_multiple_soft(self):
        """Test if multiple soft limit arguments are wrong."""
        mock_cliargs = ["rtprio=99", "memlock102400"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400"
        self.assertFalse(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_wrong_single_hard(self):
        """Test if single hard limit arguments are wrong."""
        mock_cliargs = ["nofile=1024:524288:"]
        expected = " --ulimit nofile=1024:524288"
        self.assertFalse(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_wrong_multiple_hard(self):
        """Test if multiple hard limit arguments are wrong."""
        mock_cliargs = ["nofile1024524288", "rtprio=90:99"]
        expected = " --ulimit nofile=1024:524288 --ulimit rtprio=90:99"
        self.assertFalse(*self._is_arg_translation_ok(mock_cliargs, expected))

    def test_args_wrong_multiple_mix(self):
        """Test if multiple mixed limit arguments are wrong."""
        mock_cliargs = ["rtprio=:", "memlock102400", "nofile1024:524288:"]
        expected = " --ulimit rtprio=99 --ulimit memlock=102400 --ulimit nofile=1024:524288"
        self.assertFalse(*self._is_arg_translation_ok(mock_cliargs, expected))
