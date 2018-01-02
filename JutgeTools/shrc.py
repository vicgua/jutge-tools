from enum import Enum
from shlex import quote
import sys
import os.path
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

def shrc(shell, quiet=False, alias=None, p1_alias=True, config=None,
         compiler='g++'):
    if config is not None and alias is None:
        alias = os.path.basename(sys.argv[0])
    if not quiet:
        print('Append the following to {}:'.format(_SHELL_CONFIGS[shell]))
    if p1_alias:
        print(_create_alias(shell, 'p1++', compiler + ' ' + COMPILE_FLAGS))
    if config is not None:
        print(_create_alias(shell, alias,
              os.path.basename(sys.argv[0]) + ' --config ' + config))


def _parse_args(config):
    d = {
        'shell': config['shell'],
        'quiet': config.getboolean('quiet', False),
        'compiler': config.get('compiler', 'g++'),
        # Do not convert to string if not set
        'config': str(config.file) if config.file is not None else None,
        'alias': config.get('alias', os.path.basename(sys.argv[0])),
        'p1_alias': config.getboolean('p1_alias', True)
    }

    def exc():
        return shrc(**d)
    return exc
