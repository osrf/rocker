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
import pkgutil
from pathlib import Path

import subprocess

import distro

def name_to_argument(name):
    return '--%s' % name.replace('_', '-')

class RockerExtension(object):

    def precondition_environment(self, cliargs):
        """Modify the local environment such as setup tempfiles"""
        pass

    def validate_environment(self, cliargs):
        """ Check that the environment is something that can be used.
        This will check that we're on the right base OS and that the 
        necessary resources are available, like hardware."""
        pass

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        return ''

    def get_name(self, cliargs):
        raise NotImplementedError
    
    def get_docker_args(self, cliargs):
        return ''

    @staticmethod
    def register_arguments(parser):
        raise NotImplementedError

class DevHelpers(RockerExtension):
    @staticmethod
    def get_name():
        return 'dev_helpers'

    def __init__(self):
        self.env_subs = None
        self.name = DevHelpers.get_name()


    def get_environment_subs(self):
        if not self.env_subs:
            self.env_subs = {}
            self.env_subs['user_id'] = os.getuid()
            self.env_subs['username'] = getpass.getuser()
        return self.env_subs

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(name_to_argument(DevHelpers.get_name()),
            action='store_true',
            help="add development tools emacs and byobu to your environment")


class Nvidia(RockerExtension):
    @staticmethod
    def get_name():
        return 'nvidia'

    def __init__(self):
        self.env_subs = None
        self.name = Nvidia.get_name()
        self.xauth = '/tmp/.docker.xauth'
        self.supported_versions = ['16.04', '18.04']


    def get_environment_subs(self):
        if not self.env_subs:
            self.env_subs = {}
            self.env_subs['user_id'] = os.getuid()
            self.env_subs['username'] = getpass.getuser()
            self.env_subs['DISPLAY'] = os.getenv('DISPLAY')
            self.env_subs['distro_id'] = distro.id()
            if self.env_subs['distro_id'] != 'ubuntu':
                print("WARNING distro id %s not supported by Nvidia " % self.env_subs['distro_id'])
                sys.exit(1)
            self.env_subs['distro_version'] = distro.version()
            if self.env_subs['distro_version'] not in self.supported_versions:
                print("WARNING distro version %s not in supported list by Nvidia " % self.env_subs['distro_id'])
                sys.exit(1)
                # TODO(tfoote) add a standard mechanism for checking preconditions and disabling plugins

        return self.env_subs

    def get_preamble(self, cliargs):
        preamble = pkgutil.get_data('rocker', 'templates/%s_preamble.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(preamble, self.get_environment_subs())

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    def get_docker_args(self, cliargs):
        xauth = self.xauth
        return "  -e DISPLAY -e TERM \
  -e QT_X11_NO_MITSHM=1 \
  -e XAUTHORITY=%(xauth)s -v %(xauth)s:%(xauth)s \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /etc/localtime:/etc/localtime:ro \
  --runtime=nvidia \
  --security-opt seccomp=unconfined" % locals()

    def precondition_environment(self, cliargs):
        xauth = self.xauth
        display = os.getenv('DISPLAY')
        # Make sure processes in the container can connect to the x server
        # Necessary so gazebo can create a context for OpenGL rendering (even headless)
        if not os.path.exists(self.xauth): #if [ ! -f $XAUTH ]
            Path(self.xauth).touch()
            # print("touched %s" % xauth)
        cmd = 'xauth nlist %(display)s | sed -e \'s/^..../ffff/\' | xauth -f %(xauth)s nmerge -' % locals()
        # print("runnning %s" % cmd)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as ex:
            print("Failed setting up XAuthority with command %s" % cmd)
            raise ex
        # import stat
        # Path(xauth).chmod(stat.S_IROTH) 

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(name_to_argument(Nvidia.get_name()),
            action='store_true',
            help="Enable nvidia")


class PulseAudio(RockerExtension):
    @staticmethod
    def get_name():
        return 'pulse'

    def __init__(self):
        self.env_subs = None
        self.name = PulseAudio.get_name()


    def get_environment_subs(self):
        if not self.env_subs:
            self.env_subs = {}
            self.env_subs['user_id'] = os.getuid()
            self.env_subs['XDG_RUNTIME_DIR'] = os.getenv('XDG_RUNTIME_DIR')
            self.env_subs['audio_group_id'] = grp.getgrnam('audio').gr_gid
        return self.env_subs

    def get_preamble(self, cliargs):
        return ''

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    def get_docker_args(self, cliargs):
        args = ' -v /run/user/%(user_id)s/pulse:/run/user/%(user_id)s/pulse --device /dev/snd '\
        ' -e PULSE_SERVER=unix:%(XDG_RUNTIME_DIR)s/pulse/native -v %(XDG_RUNTIME_DIR)s/pulse/native:%(XDG_RUNTIME_DIR)s/pulse/native --group-add %(audio_group_id)s '
        return args % self.get_environment_subs()

    def precondition_environment(self, cliargs):
        pass

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(name_to_argument(PulseAudio.get_name()),
            action='store_true',
            help="mount pulse audio devices")


class HomeDir(RockerExtension):
    @staticmethod
    def get_name():
        return 'home'

    def __init__(self):
        self.env_subs = None
        self.name = HomeDir.get_name()

    def get_docker_args(self, cliargs):
        return ' -v %s:%s ' % (Path.home(), Path.home())

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(name_to_argument(HomeDir.get_name()),
            action='store_true',
            help="mount the users home directory")


class User(RockerExtension):
    @staticmethod
    def get_name():
        return 'user'

    def get_environment_subs(self):
        if not self.env_subs:
            self.env_subs = {}
            self.env_subs['user_id'] = os.getuid()
            self.env_subs['username'] = getpass.getuser()
        return self.env_subs

    def __init__(self):
        self.env_subs = None
        self.name = User.get_name()

    def get_snippet(self, cliargs):
        snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % self.name).decode('utf-8')
        return em.expand(snippet, self.get_environment_subs())

    @staticmethod
    def register_arguments(parser):
        parser.add_argument(name_to_argument(User.get_name()),
            action='store_true',
            help="mount the users home directory")


