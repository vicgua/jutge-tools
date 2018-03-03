from string import Template
from pathlib import Path
import shlex
import subprocess
from enum import Enum
from ._aux.errors import CompileError
from ._aux.config_file import ConfigFile

COMPILE_FLAGS = ('-Wall -Wextra -Werror -Wno-uninitialized'
                 ' -Wno-sign-compare -Wshadow')

VALID_STANDARDS = ('c++98', 'c++03', 'c++11', 'c++14')

# Avoid clash with built-in "compile"
def compilef(strict=True, debug=True, compiler=None, standard='c++11',
             sources=''):
    if compiler is None:  # TODO: Clean redundant checks
        compiler = 'g++ -o $output $flags $sources'
    print('Compiling...')
    cwd = Path.cwd()
    if not sources:
        sources = list(cwd.glob('*.cc'))
    if not sources:
        raise CompileError('no C++ files (must end in .cc)')
    compiler_tpl = Template(compiler)
    output = Path(cwd.name.split('_')[0]).with_suffix('.x')
    if standard not in VALID_STANDARDS:
        raise ValueError(standard + ' is not a recognised standard. Valid'
                                    ' values are ' + str(VALID_STANDARDS))
    flags = ['-std=' + str(standard)]
    if debug:
        flags += shlex.split('-g -D_GLIBCXX_DEBUG -O0')
    else:
        flags += shlex.split('-DNDEBUG -O2')

    if strict:
        flags += shlex.split(COMPILE_FLAGS)

    sources_subs = map(lambda f: shlex.quote(str(Path(f).resolve())), sources)

    try:
        compiler_cmd = compiler_tpl.substitute(
            output=shlex.quote(str(output)), flags=' '.join(flags),
            sources=' '.join(sources_subs)
        )
    except KeyError as ex:
        raise CompileError('{} is not a valid variable'.format(ex))

    print('> ' + compiler_cmd)
    try:
        subprocess.check_call(compiler_cmd, shell=True)
    except subprocess.CalledProcessError as ex:
        raise CompileError('compiled exited with status ' +
                           str(ex.returncode))
    print('Compiled successfully')

def _parse_args(config):
    d = {
        'strict': config['compiler.strict'],
        'debug': config['compiler.debug'],
        'compiler': config['compiler.cmd'],
        'standard': config['compiler.standard'],
        'sources': config['_arg.sources']
    }

    def exc():
        return compilef(**d)
    return exc

def _setup_parser(parent):
    compile_parser = parent.add_parser(
        'compile', aliases=['c'],
        description='Compile the exercise in the current dir.',
        help='compile the current exercise, but do not test it'
    )
    compile_parser.set_defaults(action=_parse_args)

    compile_parser.add_argument(
        '--no-strict',
        action='store_false',
        dest=ConfigFile.argname('compiler.strict'),
        help='do not use strict flags'
    )

    compile_parser.add_argument(
        '-c', '--compiler',
        dest=ConfigFile.argname('compiler.cmd'),
        help='compiler to be used. Must support g++-like flags. Default: g++'
    )

    compile_parser.add_argument(
        '-std', '--standard',
        choices=VALID_STANDARDS,
        dest=ConfigFile.argname('compiler.standard'),
        help='C++ standard'
    )

    compile_parser.add_argument(
        '--no-debug',
        action='store_false',
        dest=ConfigFile.argname('compiler.debug'),
        help='do not include debugging symbols (and add -DNDEBUG -O2)'
    )

    compile_parser.add_argument(
        ConfigFile.argname('_arg.sources'),
        metavar='source',
        nargs='*',
        help='if specified, only these files will be compiled'
    )

    return compile_parser
