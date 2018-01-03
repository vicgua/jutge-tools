import argparse
import pkg_resources
import sys
import os.path

from ..download import _setup_parser as download_sp
from ..compilef import _setup_parser as compile_sp
from ..test import _setup_parser as test_sp
from ..skel import _setup_parser as skel_sp
from ..shrc import Shells, _setup_parser as shrc_sp
from ..debug import _setup_parser as debug_sp
from ..genconfig import _setup_parser as genconfig_sp

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

    download_sp(subparsers)
    compile_sp(subparsers)
    test_sp(subparsers)
    debug_sp(subparsers)
    skel_sp(subparsers)
    shrc_sp(subparsers)
    genconfig_sp(subparsers)

    args = parser.parse_args()
    if 'action' not in args:
        parser.print_usage()
        return
    config = ConfigFile(args)
    fn = args.action(config)
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
