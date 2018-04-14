from string import Template
from pathlib import Path
import shlex
import subprocess
import os
from enum import Enum
from ._aux.errors import CompileError
from ._aux.config_file import ConfigFile
from ._aux.print_cmd import print_cmd

COMPILE_FLAGS = ['-Wall', '-Wextra', '-Werror', '-Wno-uninitialized',
                 '-Wno-sign-compare', '-Wshadow']

VALID_STANDARDS = ('c++98', 'c++03', 'c++11', 'c++14')

# Avoid clash with built-in "compile"
def compilef(strict=True, debug=True, compiler='g++', make='make',
             standard='c++11', sources=None, flags=''):
    """Compile a problem.
        strict: Whether to enable strict checks (-Werror...)
        debug: Whether to enable debug output (-g, -O0...)
        compiler: The C++ compiler to use. Must have g++-compatible flags.
        make: If a Makefile is found, this program will be used to run it.
        standard: C++ standard to use.
        sources:
            - If no Makefile exists: the sources to pass to the compiler.
                - Empty: compile all *.cc files.
            - With a Makefile: the name of the *targets* to compile.
                - Empty: use the default target (usually "all")
        flags: A string of additional flags to be added before
                JutgeTools' flags
        """
    print('Compiling...')
    if sources is None:
        sources = []
    if standard not in VALID_STANDARDS:
        raise ValueError(standard + ' is not a recognised standard. Valid'
                                    ' values are ' + str(VALID_STANDARDS))
    flags = shlex.split(flags)
    flags += ['-std=' + str(standard)]
    if debug:
        flags += ['-g', '-D_GLIBCXX_DEBUG', '-O0']
    else:
        flags += ['-DNDEBUG', '-O2']

    if strict:
        flags += COMPILE_FLAGS

    cwd = Path.cwd()

    if (cwd / 'Makefile').exists():
        make_cmd = [make]
        new_env = {'CXX': compiler, 'CXXFLAGS': ' '.join(flags)}
        print_cmd(make_cmd, shell=False, env=new_env)
        try:
            # {**os.environ, 'CXX': compiler,
            # 'CXXFLAGS': ' '.join(flags)}  # (Python >= 3.5)
            subprocess.check_call(make_cmd, shell=False,
                env=dict(os.environ, **new_env))
        except subprocess.CalledProcessError as ex:
            raise CompileError('make exited with status ' +
                               str(ex.returncode))

    else:  # No Makefile
        if not sources:
            sources = list(cwd.glob('*.cc'))
        if not sources:
            raise CompileError('no C++ files (must end in .cc)')
        output = Path(cwd.name.split('_')[0]).with_suffix('.x')

        sources_subs = map(lambda f: str(Path(f).relative_to(cwd)),
                            sources)

        # compiler_cmd = [compiler, *flags, '-o', str(output),
        #                 *sources_subs]  # (Python >= 3.5)
        compiler_cmd = ([compiler] + flags + ['-o', str(output)] +
                        list(sources_subs))

        print_cmd(compiler_cmd, shell=False)
        try:
            subprocess.check_call(compiler_cmd, shell=False)
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

    strict_group = compile_parser.add_mutually_exclusive_group()
    strict_group.add_argument(
        '--strict',
        action='store_true',
        dest=ConfigFile.argname('compiler.strict'),
        help='use strict flags (default)'
    )
    strict_group.add_argument(
        '--no-strict',
        action='store_false',
        dest=ConfigFile.argname('compiler.strict'),
        help='do not use strict flags'
    )

    compile_parser.add_argument(
        '--compiler',
        dest=ConfigFile.argname('compiler.cmd'),
        metavar='COMPILER',
        help='compiler to be used. Must support g++-like flags. Default: g++'
    )

    compile_parser.add_argument(
        '--make',
        dest=ConfigFile.argname('compiler.make'),
        metavar='MAKE',
        help=('name of the make program (in most systems, the default should'
              ' be used; Requires GNU make). Default: make')
    )

    compile_parser.add_argument(
        '-std', '--standard',
        choices=VALID_STANDARDS,
        dest=ConfigFile.argname('compiler.standard'),
        help='C++ standard'
    )

    debug_group = compile_parser.add_mutually_exclusive_group()

    debug_group.add_argument(
        '-d', '--debug',
        action='store_true',
        dest=ConfigFile.argname('compiler.debug'),
        help=('include debugging symbols (and add -O2 and other debug flags)'
              ' (default)')
    )
    debug_group.add_argument(
        '-D', '--no-debug',
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
