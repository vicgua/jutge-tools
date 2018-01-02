from enum import Enum
from shlex import quote
import sys
import os.path
from textwrap import dedent as _dedent
from .compilef import COMPILE_FLAGS

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
            # Download a Jutge problem and change to it
            %(fname)s () {
                %(jt)s download $@ && cd $(%(jt)s dl --get-dest $@)
            }
            '''
    elif shell == Shells.TCSH:
        s = '''\
            : Download a Jutge problem and change to it
            alias %(fname)s '%(jt)s download \\!* && cd `%(jt)s --get-dest \\!*`
            '''
    elif shell == Shells.FISH:
        s = '''\
            function %(fname)s --description \\
                '# Download a Jutge problem and change to it'
                %(jt)s download $argv; and cd (%(jt)s dl --get-dest $argv)
            end
            '''
    return _dedent(s)

def _header(shell, comment):
    if shell in (Shells.BASH, Shells.ZSH, Shells.FISH):
        return '### {} ###'.format(comment)
    elif shell == Shells.TCSH:
        # The second of each is a semicolon, because tcsh's comment is a SINGLE
        # semicolon
        return ':;: {} :;:'.format(comment)

def shrc(shell, quiet=False, alias=None, p1_alias=True, config=None,
         compiler='g++', dlalias=None):
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
    if dlalias is not None:
        print(_dl_function(shell) % {'fname': dlalias, 'jt': alias})
    print()


def _parse_args(config):
    d = {
        'shell': config['shell'],
        'quiet': config.getboolean('quiet', False),
        'compiler': config.get('compiler', 'g++'),
        # Do not convert to string if not set
        'config': str(config.file) if config.file is not None else None,
        'alias': config.get('alias', os.path.basename(sys.argv[0])),
        'p1_alias': config.getboolean('p1_alias', True),
        'dlalias': config.get('dlalias')
    }

    def exc():
        return shrc(**d)
    return exc
