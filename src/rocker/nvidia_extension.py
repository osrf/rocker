# Copyright 2019 Open Source Robotics Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import grp
import os
import em
import getpass
import tempfile
from packaging.version import Version
import pkgutil
from pathlib import Path
import subprocess
import sys

from .os_detector import detect_os

from .extensions import name_to_argument
from .core import get_docker_client
from .core import RockerExtension

def get_docker_version():
    docker_version_raw = get_docker_client().version()['Version']
    # Fix for version 17.09.0-ce
    return Version(docker_version_raw.split('-')[0])

class X11(RockerExtension):
    @staticmethod
    def get_name():
        return 'x11'

    def __init__(self):
        self.name = X11.get_name()
        self._env_subs = None
        self._xauth = tempfile.NamedTemporaryFile(prefix='.docker', suffix='.xauth')

    def get_docker_args(self, cliargs):
        xauth = self._xauth.name
        return "  -e DISPLAY -e TERM \
  -e QT_X11_NO_MITSHM=1 \
  -e XAUTHORITY=%(xauth)s -v %(xauth)s:%(xauth)s \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /etc/localtime:/etc/localtime:ro " % locals()

    def precondition_environment(self, cliargs):
        xauth = self._xauth.name
        display = os.getenv('DISPLAY')
        # Make sure processes in the container can connect to the x server
        # Necessary so gazebo can create a context for OpenGL rendering (even headless)
        if not os.path.exists(xauth): #if [ ! -f $XAUTH ]
            Path(xauth).touch()
            # print("touched %s" % xauth)
        cmd = 'xauth nlist %(display)s | sed -e \'s/^..../ffff/\' | xauth -f %(xauth)s nmerge -' % locals()
        # print("runnning %s" % cmd)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as ex:
            print("Failed setting up XAuthority with command %s" % cmd)
            raise ex

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(X11.get_name()),
            action='store_true',
            default=defaults.get(X11.get_name(), None),
            help="Enable x11")


class Nvidia(RockerExtension):
    @staticmethod
    def get_name():
        return 'nvidia'

    def __init__(self):
        self._env_subs = None
        self.name = Nvidia.get_name()
        self.supported_distros = ['Ubuntu', 'Debian GNU/Linux']
        self.supported_versions = ['16.04', '18.04', '20.04', '10']


    def get_environment_subs(self, cliargs={}):
        if not self._env_subs:
            self._env_subs = {}
            self._env_subs['user_id'] = os.getuid()
            self._env_subs['username'] = getpass.getuser()
        
        # non static elements test every time
        detected_os = detect_os(cliargs['base_image'], print, nocache=cliargs.get('nocache', False))
        if detected_os is None:
            print("WARNING unable to detect os for base image '%s', maybe the base image does not exist" % cliargs['base_image'])
            sys.exit(1)
        dist, ver, codename = detected_os

        self._env_subs['image_distro_id'] = dist
        if self._env_subs['image_distro_id'] not in self.supported_distros:
            print("WARNING distro id %s not supported by Nvidia supported " % self._env_subs['image_distro_id'], self.supported_distros)
            sys.exit(1)
        self._env_subs['image_distro_version'] = ver
        if self._env_subs['image_distro_version'] not in self.supported_versions:
            print("WARNING distro %s version %s not in supported list by Nvidia supported versions" % (dist, ver), self.supported_versions)
            sys.exit(1)
            # TODO(tfoote) add a standard mechanism for checking preconditions and disabling plugins

        return self._env_subs

    def get_preamble(self, cliargs):
        preamble = pkgutil.get_data('rocker', 'templates/%s_preamble.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(preamble, self.get_environment_subs(cliargs))

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs(cliargs))

    def get_docker_args(self, cliargs):
        if get_docker_version() >= Version("19.03"):
            return "  --gpus all"
        return "  --runtime=nvidia"

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(name_to_argument(Nvidia.get_name()),
            action='store_true',
            default=defaults.get(Nvidia.get_name(), None),
            help="Enable nvidia")


