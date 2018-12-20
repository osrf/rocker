#!/usr/bin/env python3

import argparse
import os
import getpass
import sys

import pkgutil
import subprocess
import tempfile

import em

import docker
import requests
import pexpect

from pathlib import Path

class Extensions(object):
    def __init__(self, name):
        self.name = name
        expansion_dict = {}
        expansion_dict['user_id'] = os.getuid()
        expansion_dict['username'] = getpass.getuser()
        try:
            preamble = pkgutil.get_data('rocker', 'templates/%s_preamble.Dockerfile.em' % name).decode('utf-8')
            self.preamble = em.expand(preamble, expansion_dict)
        except FileNotFoundError as ex:
            self.preamble = ''
        try:
            snippet = pkgutil.get_data('rocker', 'templates/%s_snippet.Dockerfile.em' % name).decode('utf-8')
            self.snippet = em.expand(snippet, expansion_dict)
        except FileNotFoundError as ex:
            self.snippet = ''
        # try:
        #     self.debian_packages = pkgutil.get_data('rocker', 'templates/%s_debian_packages.list.em' % name).decode('utf-8')
        # except FileNotFoundError as ex:
        #     self.debian_packages = ''



class DockerImageGenerator(object):
    def __init__(self, dockerfile, image_name):
        self.dockerfile = dockerfile
        self.built = False
        self.image_name = image_name
    
    def build(self):
        with tempfile.TemporaryDirectory() as td:
            df = os.path.join(td, 'Dockerfile')
            print("Writing dockerfile to %s" % df)
            with open(df, 'w') as fh:
                fh.write(self.dockerfile)
            print('vvvvvv')
            print(self.dockerfile)
            print('^^^^^^')
            cmd = 'docker build -t %s %s' %  (self.image_name, td)
            try:
                print(cmd)
                result = subprocess.check_output(cmd, shell=True).decode('utf-8')
                print(result)
            except subprocess.CalledProcessError as ex:
                print("Docker build failed\n", ex)
                print(ex.output)
                return False

        self.built = True
        return True

    def run(self, command=[], **kwargs):
        if not self.built:
            print("Cannot run if build has not passed.")
            return False
        docker_args = ''
        if kwargs.get('nvidia', False):
            xauth = '/tmp/.docker.xauth'
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
            # import stat
            # Path(xauth).chmod(stat.S_IROTH)   
            docker_args += "  -e DISPLAY -e TERM \
  -e QT_X11_NO_MITSHM=1 \
  -e XAUTHORITY=%(xauth)s -v %(xauth)s:%(xauth)s \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /etc/localtime:/etc/localtime:ro \
  --runtime=nvidia \
  --security-opt seccomp=unconfined" % locals()
        
        if kwargs.get('home', False):
            docker_args += ' -v %s:%s ' % (Path.home(), Path.home())
        if kwargs.get('network', False):
            docker_args += ' --network %s ' % network
        if kwargs.get('pulse_audio', False):
            sub_args = {}
            sub_args['user_id'] = os.getuid()
            docker_args += ' -v /run/user/%(user_id)s/pulse:/run/user/%(user_id)s/pulse' % sub_args

        image = self.image_name
        cmd="docker run -it \
  --rm \
  %(docker_args)s \
  %(image)s %(command)s" % locals()
#   $DOCKER_OPTS \
        try:
            if kwargs.get('execute', False):
                print("Executing command: ")
                print(cmd)
                p = pexpect.spawn(cmd)
                p.interact()
            else:
                print("Run this command: \n\n\n")
                print(cmd)
        except subprocess.CalledProcessError as ex:
            print("Docker run failed\n", ex)
            print(ex.output)
            return False


def generate_dockerfile(extensions, base_image):
    dockerfile_str = ''
    for el in extensions:
        dockerfile_str += '# Preamble from extension [%s]\n' % el.name
        dockerfile_str += el.preamble + '\n'
    dockerfile_str += '\nFROM %s\n' % base_image
    for el in extensions:
        dockerfile_str += '# Snippet from extension [%s]\n' % el.name
        dockerfile_str += el.snippet + '\n'
    return dockerfile_str


def main():

    parser = argparse.ArgumentParser(description='A tool for running docker with extra options')
    parser.add_argument('image', nargs='+')
    parser.add_argument('--extensions', action='append', default=[])
    parser.add_argument('--nvidia', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--user', action='store_true')
    parser.add_argument('--home', action='store_true')
    parser.add_argument('--pull', action='store_true')
    parser.add_argument('--network', choices=['bridge', 'host', 'overlay', 'none'])
    parser.add_argument('--pulse-audio', action='store_true')

    args = parser.parse_args()

    extensions = []
    if args.nvidia and 'nvidia' not in args.extensions:
        extensions.append(Extensions('nvidia'))
        print("Added nvidia extension automatically")
    for extension in args.extensions:
        extensions.append(Extensions(extension))
    # Pulse must be before user for snippet ordering as root
    if args.pulse_audio:
        extensions.append(Extensions('pulse'))
        if 'user' not in args.extensions:
            extensions.append(Extensions('user'))
            args.extensions.append('user')
    if args.user and 'user' not in args.extensions:
        args.extensions.append('user')
        extensions.append(Extensions('user'))
    if args.home:
        if 'user' not in args.extensions:
            extensions.append(Extensions('user'))
            args.extensions.append('user')


    base_image = args.image[0]

    if args.pull:
        docker_client = docker.APIClient()
        try:
            docker_client.pull(base_image)
        except requests.exceptions.HTTPError as ex:
            print('Pull of %s failed: %s' % (base_image, ex))
            pass
    df = generate_dockerfile(extensions, base_image)
    # print(df)
    image_name = "rocker_" + base_image
    if args.extensions:
        image_name += "_%s" % '_'.join(args.extensions)
    dig = DockerImageGenerator(df, image_name)
    dig.build()
    dig.run(command=' '.join(args.image[1:]), **vars(args))
    return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
