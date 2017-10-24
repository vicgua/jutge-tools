from pathlib import Path
from .errors import SkelError
from .file_templates import *

def skel(dirname=None, files=None):
    if dirname is not None:
        dest = Path.cwd() / dirname
        try:
            dest.mkdir(exist_ok=True)
        except FileExistsError:
            raise SkelError(dirname + ' already exists and is not a dir')
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
        f_path.write_text(text)

def _parse_args(args):
    d = {
        'dirname': args.dest,
        'files': args.files
    }

    def exc():
        return skel(**d)
    return exc