from pathlib import Path
from string import Template
import shlex
import pkg_resources
from ._aux.errors import SkelError
from ._aux.file_templates import *
from ._aux.config_file import ConfigFile, process_args


def _transform_file_list(l, root, extension=None):
    '''Transform a list of Paths to a list of strings
        suitable for a Makefile.

        l: list of Paths
        root: all paths will be relative to `root` dir
        extension: new extension (with the '.') or None to leave unchanged
    '''
    if extension is not None:
        l = map(lambda p: p.with_suffix(extension), l)
    return ' '.join(map(str, map(lambda p: p.relative_to(root), l)))


def skel(
    dirname=None, files=None, makefile=None, doxygen=None, *, config=None
):
    args = [('skel.makefile', makefile), ('skel.doxygen', doxygen)]
    makefile, doxygen = process_args(config, args)
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

    tar_files = []
    source_files = []

    for f in files:
        f_path = dest / f
        if f_path.exists():
            continue  # Do not overwrite existing files
        if f_path.suffix == '.hh':
            macroname = f_path.name.upper().replace('.', '_')
            text = header_template(macroname)
        elif f_path.with_suffix('.hh').name in files:
            header = f_path.with_suffix('.hh').name
            text = source_template(header)
            source_files.append(f_path)
        elif f_path.name == 'main.cc':
            text = main_template()
            source_files.append(f_path)
        else:
            text = source_no_header_template()
            source_files.append(f_path)
        with f_path.open('w') as fobj:
            fobj.write(text)
        tar_files.append(f_path)

    if makefile:
        sed_pattern = pkg_resources.resource_string(
            __name__, 'data/prefix.sed'
        ).decode('utf-8')
        make_sed_pattern = ' \\\n'.join(
            map(shlex.quote, filter(None, sed_pattern.split('\n')))
        )
        makefile_path = dest / 'Makefile'
        if not makefile_path.exists():
            makefile_template = pkg_resources.resource_string(
                __name__, 'data/Makefile'
            ).decode('utf-8')
            makefile_string = makefile_template.format(
                sed_pattern=make_sed_pattern,
                enable_doxygen='true' if doxygen else 'false'
            )
            with makefile_path.open('w') as fobj:
                fobj.write(makefile_string)
        build_conf_path = dest / 'build_conf.mk'
        if not build_conf_path.exists():
            build_conf_template = Template(
                pkg_resources.resource_string(__name__, 'data/build_conf.mk'
                                              ).decode('utf-8')
            )
            build_conf_string = build_conf_template.substitute({
                'default_programname':
                    'program',
                'default_objects':
                    _transform_file_list(source_files, dest, '.o'),
                'default_tarname':
                    'program.tar',
                'default_tarfiles':
                    _transform_file_list(tar_files, dest)
            })
            with build_conf_path.open('w') as fobj:
                fobj.write(build_conf_string)

    if doxygen:
        doxygen_path = dest / 'Doxyfile'
        if not doxygen_path.exists():
            doxygen_template = Template(
                pkg_resources.resource_string(__name__,
                                              'data/Doxyfile').decode('utf-8')
            )
            doxygen_string = doxygen_template.substitute(problem_num=dest.name)
            with doxygen_path.open('w') as fobj:
                fobj.write(doxygen_string)


def _parse_args(config):
    def exc():
        return skel(
            dirname=config['_arg.dest'],
            files=config['_arg.files'],
            config=config
        )

    return exc


def _setup_parser(parent):
    skel_parser = parent.add_parser(
        'skel',
        description='Create a skeleton file structure',
        help='create a skeleton file structure'
    )
    skel_parser.set_defaults(action=_parse_args)

    skel_parser.add_argument(
        '-o',
        '--output',
        '--dest',
        dest=ConfigFile.argname('_arg.dest'),
        metavar='DEST_DIR',
        help='destination folder'
    )
    skel_parser.add_argument(
        '-f',
        '--files',
        nargs='+',
        metavar='FILE',
        default=None,
        dest=ConfigFile.argname('_arg.files'),
        help='files to create. Default: main.cc',
    )
    makefile_group = skel_parser.add_mutually_exclusive_group()
    makefile_group.add_argument(
        '-M',
        '--no-makefile',
        action='store_false',
        dest=ConfigFile.argname('skel.makefile'),
        help=(
            'do not use a Makefile (this is the default, use to override '
            'config)'
        )
    )
    makefile_group.add_argument(
        '-m',
        '--makefile',
        action='store_true',
        dest=ConfigFile.argname('skel.makefile'),
        help='use a Makefile.'
    )

    doxygen_group = skel_parser.add_mutually_exclusive_group()
    doxygen_group.add_argument(
        '-d',
        '--doxygen',
        action='store_true',
        dest=ConfigFile.argname('skel.doxygen'),
        help='enable Doxygen support'
    )
    doxygen_group.add_argument(
        '-D',
        '--no-doxygen',
        action='store_false',
        dest=ConfigFile.argname('skel.doxygen'),
        help='disable Doxygen support (default)'
    )

    return skel_parser
