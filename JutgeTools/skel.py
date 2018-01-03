from pathlib import Path
from ._aux.errors import SkelError
from ._aux.file_templates import *

def skel(dirname=None, files=None):
    if dirname is not None:
        dest = Path.cwd() / dirname
        if dest.exists() and not dest.is_dir():
            raise SkelError(dirname + ' already exists and is not a dir')
        elif not dest.exists():
            dest.mkdir()
    else:
        dest = Path.cwd()
    if files is None:
        files = ['main.cc']

    for f in files:
        f_path = dest / f
        if f_path.suffix == '.hh':
            macroname = f_path.name.upper().replace('.', '_')
            text = header_template(macroname)
        elif f_path.with_suffix('.hh').name in files:
            header = f_path.with_suffix('.hh').name
            text = source_template(header)
        elif f_path.name == 'main.cc':
            text = main_template()
        else:
            text = source_no_header_template()
        with f_path.open('w') as fobj:
            fobj.write(text)

def _parse_args(config):
    d = {
        'dirname': config.get('dest'),
        'files': config.get('files')
    }

    def exc():
        return skel(**d)
    return exc

def _setup_parser(parent):
    skel_parser = parent.add_parser(
        'skel',
        description='Create a skeleton file structure',
        help='create a skeleton file structure'
    )
    skel_parser.set_defaults(action=_parse_args)

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
