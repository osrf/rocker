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

import os
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
from .em import empy_expand

GLVND_VERSION_POLICY_LATEST_LTS='latest_lts'

NVIDIA_GLVND_VALID_VERSIONS=['16.04', '18.04','20.04', '22.04', '24.04']

def get_docker_version():
    docker_version_raw = get_docker_client().version()['Version']
    # Fix for version 17.09.0-ce
    return Version(docker_version_raw.split('-')[0])

def glvnd_version_from_policy(image_version, policy):
    # Default policy GLVND_VERSION_POLICY_LATEST_LTS
    if not policy:
        policy = GLVND_VERSION_POLICY_LATEST_LTS

    if policy == GLVND_VERSION_POLICY_LATEST_LTS:
        if image_version in ['16.04', '16.10', '17.04', '17.10']:
            return '16.04'
        if image_version in ['18.04', '18.10', '19.04', '19.10']:
            return '18.04'
        if image_version in ['20.04', '20.10', '21.04', '21.10']:
            return '20.04'
        if image_version in ['22.04', '22.10', '23.04', '23.10']:
            return '22.04'
        # 24.04 is not available yet
        # if image_version in ['24.04', '24.10', '25.04', '25.10']:
        #     return '24.04'
        return '22.04'
    return None

class X11(RockerExtension):
    @staticmethod
    def get_name():
        return 'x11'

    def __init__(self):
        self.name = X11.get_name()
        self._env_subs = None
        self._xauth = None

    def get_docker_args(self, cliargs):
        assert self._xauth, 'xauth not initialized, get_docker_args must be called after precodition_environment'
        xauth = self._xauth.name
        return "  -e DISPLAY -e TERM \
  -e QT_X11_NO_MITSHM=1 \
  -e XAUTHORITY=%(xauth)s -v %(xauth)s:%(xauth)s \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /etc/localtime:/etc/localtime:ro " % locals()

    def precondition_environment(self, cliargs):
        self._xauth = tempfile.NamedTemporaryFile(prefix='.docker', suffix='.xauth', delete=not cliargs.get('nocleanup'))
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
    def register_arguments(parser, defaults):
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
        self.supported_versions = ['16.04', '18.04', '20.04', '10', '22.04', '24.04']


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
        nvidia_glvnd_version = cliargs.get('nvidia_glvnd_version', None)
        if not nvidia_glvnd_version:
            nvidia_glvnd_version = glvnd_version_from_policy(ver, cliargs.get('nvidia_glvnd_policy', None) )
        self._env_subs['nvidia_glvnd_version'] = nvidia_glvnd_version

        return self._env_subs

    def get_preamble(self, cliargs):
        preamble = pkgutil.get_data('rocker', 'templates/%s_preamble.Dockerfile.em' % self.name).decode('utf-8')
        return empy_expand(preamble, self.get_environment_subs(cliargs))

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return empy_expand(snippet, self.get_environment_subs(cliargs))

    def get_docker_args(self, cliargs):
        force_flag = cliargs.get('nvidia', None)
        gpus_ids_flag = cliargs.get('gpus', None)
        if gpus_ids_flag is None:
            gpus_ids_flag = 'all'
        if force_flag == 'runtime':
            return "  --runtime=nvidia"
        if force_flag == 'gpus':
            return f"  --gpus {gpus_ids_flag}"
        if get_docker_version() >= Version("19.03"):
            return f"  --gpus {gpus_ids_flag}"
        return "  --runtime=nvidia"

    @staticmethod
    def register_arguments(parser, defaults):
        parser.add_argument(name_to_argument(Nvidia.get_name()),
            choices=['auto', 'runtime', 'gpus'],
            nargs='?',
            const='auto',
            default=defaults.get(Nvidia.get_name(), None),
            help="Enable nvidia. Default behavior is to pick flag based on docker version.")
        parser.add_argument('--nvidia-glvnd-version',
            choices=NVIDIA_GLVND_VALID_VERSIONS,
            default=defaults.get('nvidia-glvnd-version', None),
            help="Explicitly select an nvidia glvnd version")
        parser.add_argument('--nvidia-glvnd-policy',
            choices=[GLVND_VERSION_POLICY_LATEST_LTS],
            default=defaults.get('nvidia-glvnd-policy', GLVND_VERSION_POLICY_LATEST_LTS),
            help="Set an nvidia glvnd version policy if version is unset")

class Cuda(RockerExtension):
    @staticmethod
    def get_name():
        return 'cuda'

    def __init__(self):
        self._env_subs = None
        self.name = Cuda.get_name()
        self.supported_distros = ['Ubuntu', 'Debian GNU/Linux']
        self.supported_versions = ['20.04', '22.04', '24.04', '11', '12'] # Debian 11 and 12

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

        self._env_subs['download_osstring'] = dist.split()[0].lower()
        self._env_subs['download_verstring'] = ver.replace('.', '')
        self._env_subs['download_keyid'] = '3bf863cc'

        self._env_subs['image_distro_id'] = dist
        if self._env_subs['image_distro_id'] not in self.supported_distros:
            print("WARNING distro id %s not supported by Cuda supported " % self._env_subs['image_distro_id'], self.supported_distros)
            sys.exit(1)
        self._env_subs['image_distro_version'] = ver
        if self._env_subs['image_distro_version'] not in self.supported_versions:
            print("WARNING distro %s version %s not in supported list by Nvidia supported versions" % (dist, ver), self.supported_versions)
            sys.exit(1)
            # TODO(tfoote) add a standard mechanism for checking preconditions and disabling plugins

        return self._env_subs

    def get_preamble(self, cliargs):
        return ''
        # preamble = pkgutil.get_data('rocker', 'templates/%s_preamble.Dockerfile.em' % self.name).decode('utf-8')
        # return empy_expand(preamble, self.get_environment_subs(cliargs))

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return empy_expand(snippet, self.get_environment_subs(cliargs))

    def get_docker_args(self, cliargs):
        return ""
        # Runtime requires --nvidia option too

    @staticmethod
    def register_arguments(parser, defaults):
        parser.add_argument(name_to_argument(Cuda.get_name()),
            action='store_true',
            default=defaults.get('cuda', None),
            help="Install cuda and nvidia-cuda-dev into the container")
        
class Gpus(RockerExtension):
    @staticmethod
    def get_name():
        return 'gpus'

    def __init__(self):
        self.name = Gpus.get_name()

    def get_preamble(self, cliargs):
        return ''

    def get_docker_args(self, cliargs):
        # The gpu ids will be set in the nvidia extension, if the nvidia argument is passed.
        if cliargs.get('nvidia', None):
            return ''
        args = ''
        gpus = cliargs.get('gpus', None)
        if gpus:
            args += f' --gpus {gpus} '
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--gpus',
                            default=defaults.get('gpus', None),
                            help="Set the indices of GPUs to use")