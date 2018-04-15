from string import Template
from pathlib import Path
import shlex
import subprocess
import os
from enum import Enum
from ._aux.errors import CompileError, MakeError
from ._aux.config_file import ConfigFile, process_args
from ._aux.print_cmd import print_cmd
from ._aux.make import Makefile

COMPILE_FLAGS = [
    '-Wall', '-Wextra', '-Werror', '-Wno-uninitialized', '-Wno-sign-compare',
    '-Wshadow'
]

VALID_STANDARDS = ('c++98', 'c++03', 'c++11', 'c++14')

# Avoid clash with built-in "compile"


def compilef(
    compiler=None,
    make=None,
    debug=None,
    strict=None,
    standard=None,
    flags='',
    sources=None,
    *,
    config=None
):
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
    args = [('compiler.cmd', compiler), ('compiler.make', make),
            ('compiler.debug', debug), ('compiler.strict', strict),
            ('compiler.standard', standard), ('compiler.flags', flags)]
    compiler, make, debug, strict, standard, flags = process_args(config, args)
    print('Compiling...')
    if sources is None:
        sources = []
    if standard not in VALID_STANDARDS:
        raise ValueError(
            standard + ' is not a recognised standard. Valid'
            ' values are ' + str(VALID_STANDARDS)
        )
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
        makefile = Makefile(make, cwd / 'Makefile')
        new_env = {'CXX': compiler, 'CXXFLAGS': ' '.join(flags)}
        try:
            makefile.make_all(env=new_env, verbose=True)
        except subprocess.CalledProcessError as ex:
            raise CompileError('make exited with status ' + str(ex.returncode))

    else:  # No Makefile
        if not sources:
            sources = list(cwd.glob('*.cc'))
        if not sources:
            raise CompileError('no C++ files (must end in .cc)')
        output = Path(cwd.name.split('_')[0]).with_suffix('.x')

        sources_subs = map(lambda f: str(Path(f).relative_to(cwd)), sources)

        # compiler_cmd = [compiler, *flags, '-o', str(output),
        #                 *sources_subs]  # (Python >= 3.5)
        compiler_cmd = ([compiler] + flags + ['-o', str(output)] +
                        list(sources_subs))

        print_cmd(compiler_cmd, shell=False)
        try:
            subprocess.check_call(compiler_cmd, shell=False)
        except subprocess.CalledProcessError as ex:
            raise CompileError(
                'compiled exited with status ' + str(ex.returncode)
            )

    print('Compiled successfully')


def make_get_info(make_path, makefile):
    makefile = Makefile(make_path, makefile)
    try:
        executable = makefile.executable_name()
    except MakeError as ex:
        raise CompileError(
            'could not determine the executable name:'
            " 'make _exe_name' exited with status {}."
            ' Maybe not a JutgeTools Makefile?'.format(ex.returncode)
        )
    outdated = makefile.outdated()
    return executable, outdated


def _parse_args(config):
    def exc():
        return compilef(config=config, sources=config['_arg.sources'])

    return exc


def _setup_parser(parent, global_options):
    compile_parser = parent.add_parser(
        'compile',
        aliases=['c'],
        description='Compile the exercise in the current dir.',
        help='compile the current exercise, but do not test it'
    )
    compile_parser.set_defaults(action=_parse_args)

    compile_parser.add_argument(
        ConfigFile.argname('_arg.sources'),
        metavar='source',
        nargs='*',
        help='if specified, only these files will be compiled'
    )

    # Add the following options to the top-level parser, since they may be
    # needed when test or debug recompile the problem.
    strict_group = global_options.add_mutually_exclusive_group()
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

    global_options.add_argument(
        '--compiler',
        dest=ConfigFile.argname('compiler.cmd'),
        metavar='COMPILER',
        help='compiler to be used. Must support g++-like flags. Default: g++'
    )

    global_options.add_argument(
        '--make',
        dest=ConfigFile.argname('compiler.make'),
        metavar='MAKE',
        help=(
            'name of the make program (in most systems, the default should'
            ' be used; Requires GNU make). Default: make'
        )
    )

    global_options.add_argument(
        '-std',
        '--standard',
        choices=VALID_STANDARDS,
        dest=ConfigFile.argname('compiler.standard'),
        help='C++ standard'
    )

    debug_group = global_options.add_mutually_exclusive_group()

    debug_group.add_argument(
        '-d',
        '--debug',
        action='store_true',
        dest=ConfigFile.argname('compiler.debug'),
        help=(
            'include debugging symbols (and add -O2 and other debug flags)'
            ' (default)'
        )
    )
    debug_group.add_argument(
        '-D',
        '--no-debug',
        action='store_false',
        dest=ConfigFile.argname('compiler.debug'),
        help='do not include debugging symbols (and add -DNDEBUG -O2)'
    )

    return compile_parser
