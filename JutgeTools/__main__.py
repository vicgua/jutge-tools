import argparse
import pkg_resources
import sys
import os.path

from .download import _setup_parser as download_sp
from .compilef import _setup_parser as compile_sp
from .test import _setup_parser as test_sp
from .skel import _setup_parser as skel_sp
from .shrc import Shells, _setup_parser as shrc_sp
from .debug import _setup_parser as debug_sp
from .config import _setup_parser as config_sp
from .tar import _setup_parser as tar_sp

from ._aux.errors import *
from ._aux.config_file import ConfigFile

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
    global_options = parser.add_argument_group(
        title='global options',
        description=('These options affect more than one command. E.g.:'
                     ' compile flags are used when "test" and "debug" compile'
                     ' the problem.')
    )

    download_parser = download_sp(subparsers)
    compile_parser = compile_sp(subparsers, global_options)
    test_parser = test_sp(subparsers)
    debug_parser = debug_sp(subparsers)
    skel_parser = skel_sp(subparsers)
    tar_parser = tar_sp(subparsers)
    shrc_parser = shrc_sp(subparsers)
    config_parser = config_sp(subparsers)

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
    except ConfigError as ex:
        config_parser.error(ex)
    except ProcessError as ex:
        parser.error(ex)

if __name__ == '__main__':
    main()
