import argparse
import pkg_resources
import sys

from ..download import _parse_args as download_pa
from ..compilef import _parse_args as compile_pa
from ..test import _parse_args as test_pa
from ..skel import _parse_args as skel_pa
from ..shrc import Shells, _parse_args as shrc_pa
from ..debug import _parse_args as debug_pa
from ..genconfig import _parse_args as genconfig_pa

from .errors import *
from .config_file import ConfigFile

try:
    version = pkg_resources.require("jutge-tools")[0].version
except:
    version = '(could not determine version)'

def main():
    parser = argparse.ArgumentParser(description='Tool for helping with'
                                                 ' Jutge exercices')
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(version)
    )
    parser.add_argument(
        '--config',
        help='configuration file. Best used as an alias (see `shrc`)',
        default=None
    )
    subparsers = parser.add_subparsers(
        title='actions'
    )

    # `download` parser
    download_parser = subparsers.add_parser(
        'download', aliases=['dl'],
        description='Download and extract a problem file into the current dir',
        help='download an exercise and its test cases'
    )
    download_parser.set_defaults(action=download_pa)

    download_parser.add_argument(
        'exercise',
        help='exercise ID. E.g.: P51126_en'
    )

    download_parser.add_argument(
        '-k', '--keep-zip',
        action='store_true',
        help='do not delete the archive after deflatting'
    )

    parser_skel_group = download_parser.add_mutually_exclusive_group()
    parser_skel_group.add_argument(
        '-s', '--skel-files',
        metavar='FILENAME',
        nargs='+',
        default=[],
        help='create skel files with these names',
    )
    parser_skel_group.add_argument(
        '--cc',
        action='store_true',
        help='download .cc file attached to the problem'
    )
    parser_skel_group.add_argument(
        '-S', '--no-skel',
        action='store_false',
        dest='skel',
        help='do not create a skel file'
    )

    # `compile` parser
    compile_parser = subparsers.add_parser(
        'compile', aliases=['c'],
        description='Compile the exercise in the current dir.',
        help='compile the current exercise, but do not test it'
    )
    compile_parser.set_defaults(action=compile_pa)

    compile_parser.add_argument(
        '--no-strict',
        action='store_false',
        dest='strict',
        help='do not use strict flags'
    )

    compile_parser.add_argument(
        '-c', '--compiler',
        help='compiler to be used. Must support g++-like flags. Default: g++'
    )

    compile_parser.add_argument(
        '--no-debug',
        action='store_false',
        dest='debug',
        help='do not include debugging symbols (and add -DNDEBUG -O2)'
    )

    compile_parser.add_argument(
        'source',
        nargs='*',
        help='if specified, only these files will be compiled'
    )

    # `test` parser
    test_parser = subparsers.add_parser(
        'test', aliases=['t'],
        description='Test the exercise in the current dir and show the diff'
                    ' if a case fails.',
        help='test the current exercise with the test cases'
    )
    test_parser.set_defaults(action=test_pa)

    test_parser.add_argument(
        'case',
        nargs='*',
        help='test only this case(s). By default all cases are tested.'
             ' Specify without extension: `sample1`...'
    )

    test_compile_group = test_parser.add_mutually_exclusive_group()
    test_compile_group.add_argument(
        '-C', '--no-compile',
        action='store_false',
        dest='compile',
        help='do not recompile. Ignored if there is not an executable'
    )
    test_compile_group.add_argument(
        '--no-strict',
        action='store_false',
        dest='strict',
        help='compile with the --no-strict flag'
    )

    test_parser.add_argument(
        '--no-debug',
        action='store_false',
        dest='debug',
        help='test with -DNDEBUG (no effect with --no-compile)'
    )

    test_diff_group = test_parser.add_mutually_exclusive_group()
    test_diff_group.add_argument(
        '-D', '--no-diff',
        action='store_false',
        dest='diff',
        help='do not display a diff when test cases fail'
    )
    test_diff_group.add_argument(
        '-d', '--diff-tool',
        help='diff tool to use. "$output" and "$correct" will be substituted '
             ' (they are already quoted).'
             ' Default: `diff -y $output $correct`'
    )

    # `debug` parser
    debug_parser = subparsers.add_parser(
        'debug',
        description='Start a debugger attached to the executable',
        help='run on a debugger'
    )
    debug_parser.set_defaults(action=debug_pa)

    debug_parser.add_argument(
        '-d', '--debugger',
        help='debbugger to be used. "$exe" will be substituted '
             ' (it is already quoted).'
             ' Default: `gdb -tui $exe`'
    )

    debug_parser.add_argument(
        '--no-strict',
        action='store_false',
        dest='strict',
        help='compile with the --no-strict flag'
    )

    # `skel` parser
    skel_parser = subparsers.add_parser(
        'skel',
        description='Create a skeleton file structure',
        help='create a skeleton file structure'
    )
    skel_parser.set_defaults(action=skel_pa)

    skel_parser.add_argument(
        '-d', '--dest',
        help='destination folder'
    )
    skel_parser.add_argument(
        '-f', '--files',
        nargs='+',
        metavar='FILE',
        default=None,
        help='files to create. Default: main.cc',
    )

    # `shrc` parser
    shrc_parser = subparsers.add_parser(
        'shrc',
        description='Set up shell for development. The output of this command'
                    ' should be appended to your config file',
        help='set up shell for development'
    )
    shrc_parser.set_defaults(action=shrc_pa)

    shrc_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        dest='quiet',
        help='do not show help to install aliases'
    )

    p1_group = shrc_parser.add_mutually_exclusive_group()
    p1_group.add_argument(
        '-c', '--compiler',
        help='change base compiler for p1++. Must support g++-like flags.'
             ' Default: g++'
    )
    p1_group.add_argument(
        '--no-p1++-alias',
        action='store_false',
        dest='p1_alias',
        help='do not add an alias for p1++'
    )

    shrc_parser.add_argument(
        '--alias',
        help='with config, set the name that will be aliased to '
             ' {name} --config (config). By default, {name}'.format(
                name=sys.argv[0]
            )
    )

    shrc_parser.add_argument(
        '-s', '--shell',
        required=True,
        choices=Shells,
        type=Shells.get,
        help='shell for which a config format should be output'
    )

    genconfig_parser = subparsers.add_parser(
        'genconfig',
        description='Generate or update a config file and write it to'
                    ' the location specified by --config',
        help='generate or update a config file'
    )
    genconfig_parser.add_argument(
        '-c', '--compiler',
        help='compiler to be used. Must support g++-like flags'
    )
    genconfig_parser.add_argument(
        '-diff', '--diff-tool',
        help='diff tool to use. "$output" and "$correct" will be substituted '
             ' (they are already quoted)'
    )
    genconfig_parser.add_argument(
        '-dbg', '--debugger',
        help='debbugger to be used. "$exe" will be substituted '
             ' (it is already quoted)'
    )
    genconfig_parser.set_defaults(action=genconfig_pa)

    args = parser.parse_args()
    if 'action' not in args:
        parser.print_usage()
        return
    try:
        config = ConfigFile(args)
        fn = args.action(config)
    except AttributeError:
        raise
    try:
        fn()
    except DownloadError as ex:
        download_parser.error(ex)
    except CompileError as ex:
        compile_parser.error(ex)
    except TestError as ex:
        test_parser.error(ex)
    except ProcessError as ex:
        parser.error(ex)
