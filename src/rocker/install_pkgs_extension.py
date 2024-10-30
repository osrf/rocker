import em
import pkgutil
from rocker.extensions import RockerExtension


class InstallPkgs(RockerExtension):

    name = 'install_pkgs'

    @classmethod
    def get_name(cls):
        return cls.name

    def __init__(self):
        self._env_subs = None
        self.name = InstallPkgs.get_name()

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cli_args):
        pkgs = set(cli_args['install_pkgs'])
        args = {'packages': list(pkgs)}

        snippet = pkgutil.get_data(
            'rocker', 'templates/{}_snippet.Dockerfile.em'.format(self.name)).decode('utf-8')

        return em.expand(snippet, args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--install-pkgs',
                            nargs='+',
                            help='Installs specified packages in container')

        # todo add argument to install common development packages by category 
        # (e.g dev, debug, viz, sim, etc) that are not in the base image
