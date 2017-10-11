#!/usr/bin/env python3

import argparse
import pkg_resources

from .download import _parse_args as download_pa
from .compile import _parse_args as compile_pa
from .test import _parse_args as test_pa
from .errors import *

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

    parser_stub_group = download_parser.add_mutually_exclusive_group()
    parser_stub_group.add_argument(
        '-s', '--stub-file',
        metavar='FILENAME',
        action='append',
        default=[],
        help='create stub file with these name.'
             ' May be specified more than once',
    )
    parser_stub_group.add_argument(
        '-S', '--no-stub',
        action='store_false',
        dest='stub',
        help='do not create a stub file'
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
        dest='strict'
    )

    compile_parser.add_argument(
        'compiler',
        nargs='?',
        default='g++',
        help='compiler to be used. Must support g++-like flags. Default: g++'
    )

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
             ' Default: `diff -y -l $output $correct`'
    )

    args = parser.parse_args()
    try:
        fn = args.action(args)
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
    except AttributeError:
        parser.print_usage()