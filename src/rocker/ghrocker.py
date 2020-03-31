import argparse
import os
import shlex

from .core import DockerImageGenerator
from .core import get_rocker_version
from .core import RockerExtensionManager


def main():

    parser = argparse.ArgumentParser(
        description='A tool for building and testing gh-pages locally',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('directory')
    #parser.add_argument('command', nargs='*', default='')
    parser.add_argument('--nocache', action='store_true',
        help='Force a rebuild of the image')
    # TODO(tfoote) add prebuilt images for faster operations 
    # parser.add_argument('--develop', action='store_true',
    #    help='Build the image locally not using the prebuilt image.')
    parser.add_argument('--port', type=int, action='store', default='4000')
    parser.add_argument('--baseurl', type=str, action='store', default=None)
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s ' + get_rocker_version())
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--debug-inside', action='store_true')
    # TODO(tfoote) add verbose parser.add_argument('--verbose', action='store_true')


    extension_manager = RockerExtensionManager()
    default_args = {'ghpages': True, 'user': True, 'network': 'host'}
    extension_manager.extend_cli_parser(parser, default_args)

    args = parser.parse_args()
    args_dict = vars(args)
    args_dict['directory'] = os.path.abspath(args_dict['directory'])

    if args.build_only and args.baseurl:
        parser.error("build and baseurl options are incompatible")


    if args.build_only:
        args_dict['command'] = 'jekyll build -V --trace'
        del args_dict['network']
    else:
        args_dict['command'] = 'jekyll serve -w'
        if args.baseurl is not None:
            # Don't output to the default location if generating using a modified baseurl
            args_dict['command'] += ' --baseurl=\'{baseurl}\' -d /tmp/aliased_site'.format(**args_dict)

    active_extensions = extension_manager.get_active_extensions(args_dict)
    print("Active extensions %s" % [e.get_name() for e in active_extensions])

    dig = DockerImageGenerator(active_extensions, args_dict, 'ubuntu:bionic')

    exit_code = dig.build(**vars(args))
    if exit_code != 0:
        print("Build failed exiting")
        return exit_code

    if args.debug_inside:
        args_dict['command'] = 'bash'

    return dig.run(**args_dict)