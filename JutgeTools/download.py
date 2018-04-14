from urllib.request import urlopen
from urllib.error import HTTPError
from pathlib import Path
from zipfile import ZipFile, BadZipfile
from ._aux.errors import DownloadError
from .skel import skel
from ._aux.config_file import ConfigFile
from tarfile import TarFile, TarError

# TODO: join _download{,_cpp,_public_tar} in a single function, to avoid
# repeating yourself

def _download(exercise):
    url = "https://jutge.org/problems/{}/zip".format(exercise)
    print('Downloading ' + url)
    with open(exercise + '.zip', 'wb') as dest:
        try:
            orig = urlopen(url)
            data = orig.read(128)
            while data:
                dest.write(data)
                data = orig.read(128)
        except HTTPError as ex:
            raise DownloadError('download failed with code {} {}'.format(
                ex.code, ex.reason
            ))
        finally:
            orig.close()

def _download_cpp(exercise):
    url = "https://jutge.org/problems/{}/main/cc".format(exercise)
    print('Downloading ' + url)
    path = Path.cwd() / exercise / 'main.cc'
    with path.open('wb') as dest:
        try:
            orig = urlopen(url)
            data = orig.read(128)
            while data:
                dest.write(data)
                data = orig.read(128)
        except HTTPError as ex:
            raise DownloadError('download failed with code {} {}'.format(
                ex.code, ex.reason
            ))
        finally:
            orig.close()

def _download_public_tar(exercise):
    url = "https://jutge.org/problems/{}/public.tar".format(exercise)
    print('Downloading ' + url)
    path = Path.cwd() / exercise / 'public.tar'
    with path.open('wb') as dest:
        try:
            orig = urlopen(url)
            data = orig.read(128)
            while data:
                dest.write(data)
                data = orig.read(128)
        except HTTPError as ex:
            raise DownloadError('download failed with code {} {}'.format(
                ex.code, ex.reason
            ))

def download(exercise, keep_zip=False, cc=False, public_tar=False,
             keep_public_tar=False, skel_files=-1):
    cwd = Path.cwd()
    zipf = cwd / (exercise + '.zip')

    if zipf.exists():
        print(str(zipf.relative_to(cwd)) + ' exists, skipping download')
        zip_downloaded = False
    else:
        _download(exercise)
        zip_downloaded = True
    assert zipf.exists()

    if (cwd / exercise).exists():
        print('dir "{}" already exists, skipping unzip'.format(exercise))
    else:
        try:
            print('Extracting exercise')
            with ZipFile(str(zipf), 'r') as exczip:
                exczip.extractall()
                # While extracting zipfiles could create files in places
                # other than the expected dir (see docs for extractall),
                # I consider these files trusted.
        except BadZipfile:
            if zip_downloaded and not keep_zip:
                zipf.unlink()
            raise DownloadError(zipf.name + ' is not a valid zip file.' +
                                ' This may be because the exercise does not' +
                                ' exist or because the download failed')

    assert (cwd / exercise).exists()

    if not keep_zip:
        print('Removing zip file')
        zipf.unlink()

    if cc:
        _download_cpp(exercise)
        return

    if public_tar:
        tarf = cwd / (exercise + '-public.tar')
        if tarf.exists():
            print(str(tarf.relative_to(cwd)) + ' exists, skipping download')
            tar_downloaded = False
        else:
            _download_public_tar(exercise)
            tar_downloaded = True
        assert tarf.exists()

        try:
            with TarFile(str(tarf), 'r') as publictar:
                print('Extracting public files')
                publictar.extractall(path=str(cwd / exercise))
                # str-conversion in path needed in 3.5. Optional in 3.6
                # See comment for exczip.extractall() above
        except TarError:
            if tar_downloaded and not keep_public_tar:
                tarf.unlink()
            raise DownloadError(tarf.name + ' is not a valid tar file.' +
                                ' This may be because the exercise does not' +
                                " exist, because it doesn't have a public" +
                                '.tar file or because the download failed')
        if not keep_public_tar:
            print('Removing public.tar file')
            tarf.unlink()

    if skel_files is None:
        return

    print('Creating skel files')
    if skel_files == -1 or not skel_files:
        skel_files = None
    skel(exercise, skel_files)


def _print_dest(exc):
    p = Path.cwd() / exc
    if p.is_dir():
        print(p.absolute())
    else:
        print('{} does not exist'.format(p), file=sys.stderr)
        print('.')  # Default to current dir ('.')

def _parse_args(config):
    d = {
        'exercise': config['_arg.exercise'],
        'keep_zip': config['download.keep zip'],
        'cc': config['_arg.cc'],
        'public_tar': config['_arg.public tar'],
        'keep_public_tar': config['download.keep public tar'],
        'skel_files': (config['download.skel files']
            if config['download.skel'] else None)
    }

    def exc():
        if config['_arg.get-dest']:
            _print_dest(d['exercise'])
            return
        return download(**d)
    return exc

def _setup_parser(parent):
    download_parser = parent.add_parser(
        'download', aliases=['dl'],
        description='Download and extract a problem file into the current dir',
        help='download an exercise and its test cases'
    )
    download_parser.set_defaults(action=_parse_args)

    download_parser.add_argument(
        ConfigFile.argname('_arg.exercise'),
        metavar='exercise',
        help='exercise ID. E.g.: P51126_en'
    )

    keep_zip_group = download_parser.add_mutually_exclusive_group()
    keep_zip_group.add_argument(
        '-kz', '--keep-zip',
        action='store_true',
        dest=ConfigFile.argname('download.keep zip'),
        help='do not delete the archive after deflatting'
    )
    keep_zip_group.add_argument(
        '-rz', '--remove-zip',
        action='store_false',
        dest=ConfigFile.argname('download.keep zip'),
        help='opposite of --keep-zip'
    )

    keep_public_group = download_parser.add_mutually_exclusive_group()
    keep_public_group.add_argument(
        '-kp', '--keep-public-tar', '--keep-public',
        action='store_true',
        dest=ConfigFile.argname('download.keep public tar'),
        help='do not delete the public archive after extracting.'
             ' Useless without -p'
    )
    keep_public_group.add_argument(
        '-rp', '--remove-public-tar', '--remove-public',
        action='store_false',
        dest=ConfigFile.argname('download.keep public tar'),
        help='opposite of --keep-public-tar'
    )

    parser_skel_group = download_parser.add_mutually_exclusive_group()
    parser_skel_group.add_argument(
        '-s', '--skel-files',
        metavar='FILENAME',
        nargs='+',
        default=[],
        dest=ConfigFile.argname('download.skel files'),
        help='create skel files with these names',
    )
    parser_skel_group.add_argument(
        '--cc',
        action='store_true',
        dest=ConfigFile.argname('_arg.cc'),
        help='download .cc file attached to the problem'
    )
    parser_skel_group.add_argument(
        '-S', '--no-skel',
        action='store_false',
        dest=ConfigFile.argname('download.skel'),
        help='do not create a skel file'
    )

    download_parser.add_argument(
        '-p', '--public', '--public-tar',
        action='store_true',
        dest=ConfigFile.argname('_arg.public tar'),
        help='download the public files of the exercise (public.tar)'
    )

    download_parser.add_argument(
        '--get-dest',
        action='store_true',
        dest=ConfigFile.argname('_arg.get-dest'),
        help='get the dir where the problem resides.'
             ' Only useful for scripting'
    )

    return download_parser
