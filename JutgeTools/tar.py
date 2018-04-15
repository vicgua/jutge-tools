import argparse
import tarfile
import subprocess
from pathlib import Path
from ._aux.config_file import ConfigFile, process_arg
from ._aux.errors import TarError as JTTarError  # to avoid confusion with
                                                 # tarfile.TarError
from ._aux.errors import MakeError
from ._aux.print_cmd import print_cmd
from ._aux.make import Makefile

def _tar_filter(tarinfo):
    """This function gets a TarInfo object and outputs a filtered one.

        In this case, the TarInfo ouput will change the UID/GID
        to those of root and the permission to u=rw,g=r,o=r. Modification
        time is preserved, though
    """
    tarinfo.uname, tarinfo.uid = tarinfo.gname, tarinfo.gid = ('root', 0)
    tarinfo.mode = 0o0644  # rw-r--r--
    return tarinfo

def tar(files=None, output=None, make=None, *, config=None):
    make = process_arg(config, 'compiler.make', make)
    if output is None:
        with open('program.tar', 'wb') as f:
            return tar(files, f)
    if not files:
        if Path('Makefile').exists():
            makefile = Makefile(make, Path('Makefile'))
            try:
                makefile.make_target('tar', verbose=True)
            except MakeError as ex:
                raise JTTarError('make tar failed with status ' +
                                 str(ex.returncode))
            return
        else:
            raise JTTarError('no files specified and no Makefile found')
    try:
        with tarfile.TarFile(fileobj=output, mode='w') as tf:
            for f in files:
                tf.add(f, filter=_tar_filter)
    except FileNotFoundError as ex:
        raise JTTarError('file not found: {}'.format(ex))
    except tarfile.TarError as ex:
        raise JTTarError('tar error: {}'.format(ex))

def _parse_args(config):
    def exc():
        return tar(
            files=config['_arg.file'],
            output=config['_arg.output'],
            config=config
        )
    return exc

def _setup_parser(parent):
    tar_parser = parent.add_parser(
        'tar',
        description='Create a tar file to send to Jutge',
        help='create a tar file'
    )
    tar_parser.set_defaults(action=_parse_args)

    tar_parser.add_argument(
        '-o', '--output',
        dest=ConfigFile.argname('_arg.output'),
        metavar='FILE',
        type=argparse.FileType('wb'),
        help='name of the output file. By default, program.tar',
        default='program.tar'
    )

    tar_parser.add_argument(
        dest=ConfigFile.argname('_arg.file'),
        metavar='FILE',
        nargs='*',
        help=('file to add to the tar archive. If none are provided, a'
              ' Makefile should exists which provides `make tar` (such as'
              ' those created by `jutge-tools skel -mk`). In this case,'
              ' --output is ignored.')
    )
    return tar_parser
