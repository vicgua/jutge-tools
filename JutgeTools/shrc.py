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
            {fname} () {{
                {jt} download $@ && cd $({jt} dl --get-dest $@)
            }}
            '''
    elif shell == Shells.TCSH:
        s = '''\
            : Download a Jutge problem and cd to it
            alias {fname} '{jt} download \\!* && cd `{jt} --get-dest \\!*`
            '''
    elif shell == Shells.FISH:
        s = '''\
            function {fname} --description \\
                '# Download a Jutge problem and cd to it'
                {jt} download $argv; and cd ({jt} dl --get-dest $argv)
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

def shrc(shell, quiet=False, alias=None, p1_alias=None, p2_alias=None,
         dl_alias=None, compiler='g++'):
    if not quiet:
        print('Append the following to {}:'.format(_SHELL_CONFIGS[shell]),
                file=sys.stderr)
    print(_header(shell, 'Jutge tools'))
    if p1_alias is not None:
        print(_create_alias(shell, p1_alias, compiler + ' ' + COMPILE_FLAGS
              + '-std=c++98'))
    if p2_alias is not None:
        print(_create_alias(shell, p2_alias, compiler + ' ' + COMPILE_FLAGS
                            + '-std=c++11'))
    if dl_alias is not None:
        print(_dl_function(shell).format(
            fname=dl_alias,
            jt=os.path.basename(sys.argv[0])
        ))
    print()


def _parse_args(config):
    d = {
        'shell': config['_arg.shell'],
        'quiet': config['_arg.quiet'],
        'compiler': split(config['compiler.cmd'])[0],
        'p1_alias': config['shrc.p1++ alias'],
        'p2_alias': config['shrc.p2++ alias'],
        'dl_alias': config['shrc.dl alias']
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
        '--p1++-alias',
        metavar='alias',
        default='p1++',
        dest=ConfigFile.argname('shrc.p1++ alias'),
        help='add an alias for p1++ (strict + C++98) with this name.'
             ' By default, p1++'
    )
    p1_group.add_argument(
        '--no-p1++-alias',
        action='store_const',
        const=None,
        dest=ConfigFile.argname('shrc.p1++ alias'),
        help='do not add an alias for p1++'
    )

    p2_group = shrc_parser.add_mutually_exclusive_group()
    p2_group.add_argument(
        '--p2++-alias',
        metavar='alias',
        default='p2++',
        dest=ConfigFile.argname('shrc.p2++ alias'),
        help='add an alias for p2++ (strict + C++11) with this name.'
             ' By default, p2++'
    )
    p2_group.add_argument(
        '--no-p2++-alias',
        action='store_const',
        const=None,
        help='do not add an alias for p2++'
    )

    shrc_parser.add_argument(
        '--dlalias',
        metavar='alias',
        dest=ConfigFile.argname('shrc.dl alias'),
        help='set an alias that will download and cd into a problem'
    )

    return shrc_parser
