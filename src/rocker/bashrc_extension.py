import em
import pkgutil
import os
import urllib3
from rocker.core import get_user_name, ExtensionError
from rocker.extensions import RockerExtension


class BashrcExtensions(RockerExtension):

    name = 'bashrc_extensions'

    @classmethod
    def get_name(cls):
        return cls.name

    def __init__(self):
        self._env_subs = None
        self.name = BashrcExtensions.get_name()

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''
    
    def get_filename(self, bashrc_extension_file):
        if os.path.isfile(bashrc_extension_file):
            return os.path.join(self.name, os.path.basename(bashrc_extension_file))
        elif bashrc_extension_file.startswith(('http://', 'https://')):
            filename = os.path.basename(urllib3.util.url.parse_url(bashrc_extension_file).path)
            if not filename:
                raise ExtensionError('Bashrc extension file does not appear to have a filename: {}'.format(bashrc_extension_file))
            return os.path.join(self.name, filename)
        else:
            raise ExtensionError('Bashrc extension files is not a file or URL: {}'.format(bashrc_extension_file))

    def get_files(self, cli_args):
        files = {}
        for bashrc_extension in cli_args[self.name]:
            if os.path.isfile(bashrc_extension):
                with open(bashrc_extension, 'r') as f:
                    files[self.get_filename(bashrc_extension)] = f.read()
            elif bashrc_extension.startswith(('http://', 'https://')):
                try:
                    response = urllib3.PoolManager().request('GET', bashrc_extension)
                    if response.status != 200:
                        raise ExtensionError(f'Failed to fetch bashrc extension from URL {bashrc_extension}, status code: {response.status}')
                    files[self.get_filename(bashrc_extension)] = response.data.decode('utf-8')
                except urllib3.exceptions.HTTPError as e:
                    raise ExtensionError(f'Failed to fetch bashrc extension from URL {bashrc_extension}: {str(e)}')

        return files

    @staticmethod
    def get_home_dir(cli_args):
        if cli_args["user"]:
            return os.path.join(os.path.sep, "home", get_user_name())
        else:
            return os.path.join(os.path.sep, "root")

    def get_user_snippet(self, cli_args):
        args = {}
        args['bashrc_extension_files'] = {self.get_filename(bashrc_extension): os.path.basename(self.get_filename(bashrc_extension)) for bashrc_extension in cli_args[self.name]}
        args['home_dir'] = self.get_home_dir(cli_args)

        snippet = pkgutil.get_data(
            'rocker', 'templates/{}_user_snippet.Dockerfile.em'.format(self.name)).decode('utf-8')

        return em.expand(snippet, args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--bashrc-extensions',
                            nargs='+',
                            help="Sources custom bashrc extensions from the container's default bashrc. An extension can be a local file or a URL.")
