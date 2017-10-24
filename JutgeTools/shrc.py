from enum import Enum
from shlex import quote
from sys import stderr
from .compile import COMPILE_FLAGS

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

def _bash(info=True):
    if info:
        print('Append the following to ~/.bashrc:', file=stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))

def _tcsh(info=True):
    if info:
        print('Append the following to ~/.bashrc:', file=stderr)
    print('alias p1++ g++ ' + COMPILE_FLAGS)

def _zsh(info=True):
    if info:
        print('Append the following to ~/.zshrc:', file=stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))

def _fish(info=True):
    if info:
        print('Append the following to ~/.config/fish/config.fish:',
              file=stderr)
    print('alias p1++=', end='')
    print(quote('g++ ' + COMPILE_FLAGS))


def shrc(shell, **kwargs):
    actions = {
        Shells.BASH: _bash,
        Shells.TCSH: _tcsh,
        Shells.ZSH: _zsh,
        Shells.FISH: _fish
    }
    actions[shell](**kwargs)


def _parse_args(args):
    d = {
        'shell': args.shell,
        'info': args.info,
        'compiler': args.compiler
    }

    def exc():
        return shrc(**d)
    return exc