from enum import Enum
from shlex import quote
import sys
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

def _bash(info=True, config=None, **_):
    if info:
        print('Append the following to ~/.bashrc:', file=sys.stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))
    if config is not None:
        print('alias jutge-tools=', end='')
        print(quote('jutge-tools --config ' + config))

def _tcsh(info=True, config=None, **_):
    if info:
        print('Append the following to ~/.tcshrc:', file=sys.stderr)
    print('alias p1++ g++ ' + COMPILE_FLAGS)
    if config is not None:
        print('alias jutge-tools ', end='')
        print('jutge-tools --config ' + config)

def _zsh(info=True, config=None, **_):
    if info:
        print('Append the following to ~/.zshrc:', file=sys.stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))
    if config is not None:
        print('alias jutge-tools=', end='')
        print(quote('jutge-tools --config ' + config))

def _fish(info=True, config=None, **_):
    if info:
        print('Append the following to ~/.config/fish/config.fish:',
              file=sys.stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))
    if config is not None:
        print('alias jutge-tools=', end='')
        print(quote('jutge-tools --config ' + config))


def shrc(shell, **kwargs):
    actions = {
        Shells.BASH: _bash,
        Shells.TCSH: _tcsh,
        Shells.ZSH: _zsh,
        Shells.FISH: _fish
    }
    actions[shell](**kwargs)


def _parse_args(config):
    d = {
        'shell': config['shell'],
        'info': config.getboolean('info', True),
        'compiler': config.get('compiler', 'g++'),
        # Do not convert to string if not set
        'config': str(config.file) if config.file is not None else None
    }

    def exc():
        return shrc(**d)
    return exc
