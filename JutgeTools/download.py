from pathlib import Path
from zipfile import BadZipFile
from ._aux.errors import DownloadError
from .skel import skel
from ._aux.config_file import ConfigFile, process_arg
from tarfile import TarError
from PyJutge.problem import Problem


def download(problem_num, skel_files=None, *, config=None):
    skel_files = process_arg(config, 'download.skel files', skel_files)
    cwd = Path.cwd()
    try:
        problem = Problem(problem_num)
    except ValueError as ex:
        raise DownloadError(ex)

    if not problem.has_zip():
        raise DownloadError("this problem does not offer a downloadable zip")
    zipf = cwd / (problem_num + '.zip')
    if zipf.exists():
        print(str(zipf.relative_to(cwd)) + ' exists, skipping download')
        try:
            problem_dir = problem.extract_zip(cwd, verbose=True, tempdest=zipf)
        except BadZipFile:
            raise DownloadError('{} is not a valid zip file'.format(zipf.name))
    else:
        try:
            problem_dir = problem.extract_zip(cwd, verbose=True)
        except BadZipFile:
            # This shouldn't happen, because the Jutge file is downloaded
            # directly, and it is assumed to be correct.
            raise

    if problem.has_public_tar():
        tarf = cwd / (problem_num + '-public.tar')
        if tarf.exists():
            print(str(tarf.relative_to(cwd)) + ' exists, skipping download')
            try:
                problem.extract_public_tar(
                    problem_dir, verbose=True, tempdest=tarf
                )
            except BadZipFile:
                raise DownloadError(
                    '{} is not a valid tar file'.format(tarf.name)
                )
        else:
            try:
                problem.extract_public_tar(problem_dir, verbose=True)
            except TarError:
                # See comment above for zips
                raise

    cc_path = problem_dir / 'main.cc'
    if problem.has_cc() and not cc_path.exists():
        problem.download_cc(cc_path)

    if skel_files is None:
        return

    print('Creating skel files')
    skel(exercise, skel_files, config=config)


def _print_dest(exc):
    p = Path.cwd() / exc
    if p.is_dir():
        print(p.absolute())
    else:
        print('{} does not exist'.format(p), file=sys.stderr)
        print('.')  # Default to current dir ('.')


def _parse_args(config):
    def exc():
        if config['_arg.get-dest']:
            _print_dest(d['exercise'])
            return
        return download(
            problem_num=config['_arg.problem'],
            config=config
        )

    return exc


def _setup_parser(parent):
    download_parser = parent.add_parser(
        'download',
        aliases=['dl'],
        description='Download and extract a problem file into the current dir',
        help='download an exercise and its test cases'
    )
    download_parser.set_defaults(action=_parse_args)

    download_parser.add_argument(
        ConfigFile.argname('_arg.problem'),
        metavar='problem',
        help='problem number. E.g.: P51126_en'
    )

    parser_skel_group = download_parser.add_mutually_exclusive_group()
    parser_skel_group.add_argument(
        '-s',
        '--skel-files',
        metavar='FILENAME',
        nargs='+',
        default=[],
        dest=ConfigFile.argname('download.skel files'),
        help='create skel files with these names',
    )
    parser_skel_group.add_argument(
        '-S',
        '--no-skel',
        action='store_const',
        const=[],
        dest=ConfigFile.argname('download.skel files'),
        help='do not create a skel file'
    )

    download_parser.add_argument(
        '--get-dest',
        action='store_true',
        dest=ConfigFile.argname('_arg.get-dest'),
        help='get the dir where the problem resides.'
        ' Only useful for scripting'
    )

    return download_parser
