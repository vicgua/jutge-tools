import argparse
import tarfile
import subprocess
from pathlib import Path
from ._aux.config_file import ConfigFile
from ._aux.errors import TarError as JTTarError  # to avoid confusion with
                                                 # tarfile.TarError

def _tar_filter(tarinfo):
    """This function gets a TarInfo object and outputs a filtered one.

        In this case, the TarInfo ouput will change the UID/GID
        to those of root and the permission to u=rw,g=r,o=r. Modification
        time is preserved, though
    """
    tarinfo.uname, tarinfo.uid = tarinfo.gname, tarinfo.gid = ('root', 0)
    tarinfo.mode = 0o0644  # rw-r--r--
    return tarinfo

def tar(files=None, output=None):
    if output is None:
        with open('program.tar', 'wb') as f:
            return tar(files, f)
    if not files:
        if Path('Makefile').is_file():
            make_cmd = 'make tar'
            print('> ' + make_cmd)
            try:
                subprocess.check_call(make_cmd, shell=True)
            except subprocess.CalledProcessError as ex:
                raise JTTarError('make tar failed with status ' +
                                 str(ex.returncode))
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
    d = {
        'files': config['_arg.file'],
        'output': config['_arg.output']
    }

    def exc():
        return tar(**d)
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
