from pathlib import Path
import shlex
import subprocess
from .errors import CompileError

COMPILE_FLAGS = ('-ansi -Wall -Wextra -Werror -Wno-uninitialized'
                 ' -Wno-sign-compare -Wshadow')

def compile(strict=True, compiler='g++', sources=''):
    print('Compiling...')
    cwd = Path.cwd()
    if not sources:
        sources = map(lambda x: x.name, cwd.glob('*.cc'))
    if not sources:
        raise CompileError('no C++ files (must end in .cc)')
    args = [compiler, '-o', cwd.name.split('_')[0] + '.x']
    args += shlex.split('-DNDEBUG -O2 -std=c++11')
    if strict:
        args += shlex.split(COMPILE_FLAGS)
    
    args += map(lambda f: str(Path(f).resolve()), sources)

    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as ex:
        raise CompileError('compiler exited with status ' +
                           str(ex.returncode))
    except FileNotFoundError:
        raise CompileError(compiler +
                           ' not installed; try specifying a different'
                           ' compiler')
    print('Compiled successfully')

def _parse_args(args):
    d = {
        'strict': args.strict,
        'compiler': args.compiler,
        'sources': args.source
    }

    def exc():
        return compile(**d)
    return exc