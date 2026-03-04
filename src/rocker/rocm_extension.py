# Copyright 2025 Open Source Robotics Foundation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import getpass
import subprocess
import sys
from pathlib import Path

from .os_detector import detect_os
from .extensions import name_to_argument
from .core import RockerExtension


def has_rocm_driver():
    """
    Detect if AMD ROCm drivers are installed on the host system.
    This checks for the presence of /dev/kfd and /dev/dri/renderD128,
    which indicate that ROCm drivers are installed and functional.
    
    Returns:
        bool: True if ROCm driver devices are detected, False otherwise.
    """
    return os.path.exists('/dev/kfd') and os.path.exists('/dev/dri/renderD128')


class Rocm(RockerExtension):
    @staticmethod
    def get_name():
        return 'rocm'

    def __init__(self):
        self._env_subs = None
        self.name = Rocm.get_name()
        self.supported_distros = ['Ubuntu', 'Debian GNU/Linux']
        self.supported_versions = ['20.04', '22.04', '24.04']

    def get_environment_subs(self, cliargs={}):
        if not self._env_subs:
            self._env_subs = {}
            self._env_subs['user_id'] = os.getuid()
            self._env_subs['username'] = getpass.getuser()
            
            detected_os = detect_os(cliargs['base_image'], print, nocache=cliargs.get('nocache', False))
            if detected_os is None:
                print("WARNING unable to detect os for base image '%s', maybe the base image does not exist" % cliargs['base_image'])
                sys.exit(1)
            
            dist, ver, codename = detected_os
            self._env_subs['image_distro_id'] = dist
            self._env_subs['image_distro_version'] = ver
            
        return self._env_subs

    def validate_environment(self, cliargs, parser):
        """
        Check if ROCm drivers/hardware are available on the host.
        Provides user-facing errors for better UX.
        """
        if cliargs.get('rocm'):
            if not has_rocm_driver():
                parser.error("--rocm was specified, but no AMD ROCm drivers or devices were detected on the host.\n"
                           "  Ensure /dev/kfd and /dev/dri/renderD128 exist.\n"
                           "  The container may not have access to GPU hardware.")

    def get_docker_args(self, cliargs):
        """
        Add ROCm device mounts to docker run command.
        ROCm requires mounting /dev/kfd and /dev/dri devices for GPU access.
        Also need to add the user to the render group for permissions.
        """
        args = " --device /dev/kfd --device /dev/dri --group-add render"
        return args

    @staticmethod
    def register_arguments(parser, defaults):
        parser.add_argument(name_to_argument(Rocm.get_name()),
                          action='store_true',
                          default=defaults.get('rocm', None),
                          help="Enable ROCm support for AMD GPUs. Mounts /dev/kfd and /dev/dri devices.")
