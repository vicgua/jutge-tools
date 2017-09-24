from pathlib import Path
import shlex
import subprocess
from .errors import CompileError

def compile(strict=True, compiler='g++'):
    print('Compiling...')
    cwd = Path.cwd()
    files = map(lambda x: x.name, cwd.glob('*.cc'))
    if not files:
        raise CompileError('no C++ files (must end in .cc)')
    args = [compiler, '-o', cwd.name.split('_')[0] + '.x']
    args += shlex.split('-DNDEBUG -O2 -std=c++11')
    if strict:
        args += shlex.split('-Wall -Wextra -Werror -Wno-uninitialized '
                            '-Wno-sign-compare -Wshadow')
    
    args += map(lambda f: str(Path(f).resolve()), files)

    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as ex:
        raise CompileError('compiler exited with status ' +
                           str(ex.returncode))
    except FileNotFoundError:
        raise CompileError(compiler +
                           ' not installed; try specifying a compiler')
    print('Compiled successfully')

def _parse_args(args):
    d = {
        'strict': args.strict,
        'compiler': args.compiler
    }

    def exc():
        return compile(**d)
    return exc