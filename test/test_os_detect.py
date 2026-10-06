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

import docker
try:
    import pytest
except ImportError:
    class _MockMark:
        def __getattr__(self, name):
            return lambda func: func
    class _MockPytest:
        mark = _MockMark()
    pytest = _MockPytest()
from packaging.version import Version
import unittest
from unittest.mock import patch

from rocker.core import DependencyMissing, ImageNotFound, get_docker_client
from rocker.os_detector import detect_os, ensure_detector_image, DETECTOR_TAG, _detect_os_cache

# Small image used to exercise the pull code paths. It is removed locally before use.
AUTO_PULL_IMAGE = "alpine:3.20"


def remove_local_image(image_name):
    try:
        get_docker_client().remove_image(image_name, force=True)
    except docker.errors.ImageNotFound:
        pass
    _detect_os_cache.pop(image_name, None)


class RockerOSDetectorTest(unittest.TestCase):

    @pytest.mark.docker
    def test_ubuntu(self):
        result = detect_os("ubuntu:xenial")
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '16.04')

        result = detect_os("ubuntu:bionic")
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '18.04')

        # Cover verbose codepath
        result = detect_os("ubuntu:bionic", output_callback=print)
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '18.04')

    @pytest.mark.docker
    def test_ubuntu_focal(self):
        result = detect_os("ubuntu:focal")
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '20.04')

        # Cover verbose codepath
        result = detect_os("ubuntu:focal", output_callback=print)
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '20.04')

    @pytest.mark.docker
    def test_fedora(self):
        result = detect_os("fedora:29")
        self.assertEqual(result[0], 'Fedora')
        self.assertEqual(result[1], '29')

    @pytest.mark.docker
    def test_does_not_exist(self):
        with self.assertRaises(ImageNotFound):
            detect_os("osrf/ros:does_not_exist")

    @pytest.mark.docker
    def test_cannot_detect_os(self):
        # hello-world runs but carries no OS release information
        # Test with output callback too get coverage of error reporting
        result = detect_os("hello-world:latest", output_callback=print)
        self.assertEqual(result, None)

    @pytest.mark.docker
    def test_auto_pull(self):
        remove_local_image(AUTO_PULL_IMAGE)
        result = detect_os(AUTO_PULL_IMAGE, output_callback=print)
        self.assertEqual(result[0], 'Alpine Linux')
        self.assertTrue(result[1].startswith('3.20'))

    @pytest.mark.docker
    def test_no_auto_pull(self):
        remove_local_image(AUTO_PULL_IMAGE)
        with self.assertRaises(ImageNotFound) as cm:
            detect_os(AUTO_PULL_IMAGE, auto_pull=False)
        self.assertIn('auto-pull is disabled', str(cm.exception))
        # The image must not have been pulled
        with self.assertRaises(docker.errors.ImageNotFound):
            get_docker_client().inspect_image(AUTO_PULL_IMAGE)

    @pytest.mark.docker
    def test_detector_image_build_failure(self):
        # Tooling failure mode: helper image cannot be built
        with patch('rocker.os_detector.docker_build', return_value=None):
            with self.assertRaises(DependencyMissing):
                detect_os("ubuntu:focal", nocache=True)

    @pytest.mark.docker
    def test_docker_cli_warning_filtered(self):
        # Docker Engine < 29.7 emits "WARNING: Image mount is an experimental feature"
        # on stderr when --mount type=image is used.
        class FakeSpawn:
            exitstatus = 0

            def read(self):
                return (
                    b'WARNING: Image mount is an experimental feature\r\n'
                    b'{"name":"Ubuntu","os_release":{"VERSION_ID":"22.04","VERSION_CODENAME":"jammy"}}\r\n'
                )

            def close(self):
                pass

        _detect_os_cache.pop("ubuntu:jammy-warning-test", None)
        with patch('rocker.os_detector.base_image_exists', return_value=True), \
             patch('rocker.os_detector.ensure_detector_image', return_value=DETECTOR_TAG), \
             patch('rocker.os_detector.pexpect.spawn', return_value=FakeSpawn()):
            result = detect_os("ubuntu:jammy-warning-test")
        self.assertEqual(result, ('Ubuntu', '22.04', 'jammy'))

    # TODO: Remove this test once Docker Engine >= 28.0.0 is the minimum supported version.
    @pytest.mark.docker
    def test_legacy_docker_fallback(self):
        _detect_os_cache.pop("ubuntu:focal", None)
        with patch('rocker.os_detector._get_docker_version', return_value=Version("27.5.1")):
            result = detect_os("ubuntu:focal", output_callback=print)
        self.assertEqual(result[0], 'Ubuntu')
        self.assertEqual(result[1], '20.04')
        # Ensure the temporary per-image detector image was cleaned up
        with self.assertRaises(docker.errors.ImageNotFound):
            get_docker_client().inspect_image("rocker:os_detect_ubuntu_focal")

        # Also test failure to build the temporary per-image detector image
        _detect_os_cache.pop("ubuntu:focal", None)
        with patch('rocker.os_detector._get_docker_version', return_value=Version("27.5.1")), \
             patch('rocker.os_detector.ensure_detector_image', return_value=DETECTOR_TAG), \
             patch('rocker.os_detector.docker_build', return_value=None):
            result = detect_os("ubuntu:focal", output_callback=print)
        self.assertIsNone(result)

