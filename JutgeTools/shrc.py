from enum import Enum
from shlex import quote, split
import sys
import os.path
from textwrap import dedent as _dedent
from .compilef import COMPILE_FLAGS
from ._aux.config_file import ConfigFile

class Shells(Enum):
    BASH = 1
    TCSH = 2
    ZSH  = 3
    FISH = 4

    @classmethod
    def get(cls, name):
        return cls[name.upper()]

    def __str__(self):
        return self.name.lower()

def _create_alias(shell, name, action):
    if shell in (Shells.BASH, Shells.ZSH, Shells.FISH):
        return 'alias {n}={a}'.format(n=name, a=quote(action))
    elif shell == Shells.TCSH:
        return 'alias {n} {a}'.format(n=name, a=action)

_SHELL_CONFIGS = {
    Shells.BASH: '~/.bashrc',
    Shells.TCSH: '~/.tcshrc',
    Shells.ZSH: '~/.zshrc',
    Shells.FISH: '~/.config/fish/config.fish'
}

def _dl_function(shell):
    if shell in (Shells.BASH, Shells.ZSH):
        s = '''\
            # Download a Jutge problem and cd to it
            %(fname)s () {
                %(jt)s download $@ && cd $(%(jt)s dl --get-dest $@)
            }
            '''
    elif shell == Shells.TCSH:
        s = '''\
            : Download a Jutge problem and cd to it
            alias %(fname)s '%(jt)s download \\!* && cd `%(jt)s --get-dest \\!*`
            '''
    elif shell == Shells.FISH:
        s = '''\
            function %(fname)s --description \\
                '# Download a Jutge problem and cd to it'
                %(jt)s download $argv; and cd (%(jt)s dl --get-dest $argv)
            end
            '''
    return _dedent(s)

def _header(shell, comment):
    if shell in (Shells.BASH, Shells.ZSH, Shells.FISH):
        return '### {} ###'.format(comment)
    elif shell == Shells.TCSH:
        # The second of each is a semicolon, because tcsh's comment is a SINGLE
        # colon
        return ':;: {} :;:'.format(comment)

def shrc(shell, quiet=False, alias=None, p1_alias=True, config=None,
         compiler='g++', dl_alias=None):
    if alias is None:
        alias = os.path.basename(sys.argv[0])
    if not quiet:
        print('Append the following to {}:'.format(_SHELL_CONFIGS[shell]),
                file=sys.stderr)
    print(_header(shell, 'Jutge tools'))
    if p1_alias:
        print(_create_alias(shell, 'p1++', compiler + ' ' + COMPILE_FLAGS))
    if config is not None:
        print(_create_alias(shell, alias,
              os.path.basename(sys.argv[0]) + ' --config ' + config))
    if dl_alias is not None:
        print(_dl_function(shell) % {'fname': dl_alias, 'jt': alias})
    print()


def _parse_args(config):
    d = {
        'shell': config['_arg.shell'],
        'quiet': config['_arg.quiet'],
        'compiler': split(config['compiler.cmd'])[0],
        'config': None,  # TODO: Rework shrc
        'alias': None,  # TODO
        'p1_alias': config['shrc.p1++ alias'],
        'dlalias': config['shrc.dl alias']
    }

    def exc():
        return shrc(**d)
    return exc

def _setup_parser(parent):
    shrc_parser = parent.add_parser(
        'shrc',
        description='Set up shell for development. The output of this command'
                    ' should be appended to your config file',
        help='set up shell for development'
    )
    shrc_parser.set_defaults(action=_parse_args)

    shrc_parser.add_argument(
        '-s', '--shell',
        required=True,
        choices=Shells,
        type=Shells.get,
        dest=ConfigFile.argname('_arg.shell'),
        help='shell for which a config format should be output'
    )

    shrc_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        dest=ConfigFile.argname('_arg.quiet'),
        help='do not show help to install aliases'
    )

    p1_group = shrc_parser.add_mutually_exclusive_group()
    p1_group.add_argument(
        '-c', '--compiler',
        dest=ConfigFile.argname('compiler.cmd'),
        help='change base compiler for p1++. Must support g++-like flags.'
             ' Default: g++'
    )
    p1_group.add_argument(
        '--no-p1++-alias',
        action='store_false',
        dest=ConfigFile.argname('shrc.p1++ alias'),
        help='do not add an alias for p1++'
    )

    shrc_parser.add_argument(
        '--dlalias',
        dest=ConfigFile.argname('shrc.dl alias'),
        help='set an alias that will download and cd into a problem'
    )

    return shrc_parser
