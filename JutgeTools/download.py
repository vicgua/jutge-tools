from urllib.request import urlopen
from urllib.error import HTTPError
from pathlib import Path
from zipfile import ZipFile, BadZipfile
from ._aux.errors import DownloadError
from .skel import skel

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


def download(exercise, keep_zip=False, cc=False, skel_files=-1):
    cwd = Path.cwd()
    zipf = cwd / (exercise + '.zip')

    if zipf.exists():
        print(exercise + '.zip exists, skipping download')
        zip_downloaded = False
    else:
        _download(exercise)
        zip_downloaded = True
    assert zipf.exists()

    if (cwd / exercise).exists():
        print('dir "{}" already exists, skipping unzip'.format(exercise))
    else:
        try:
            with ZipFile(str(zipf), 'r') as exczip:
                exczip.extractall()
        except BadZipfile:
            if zip_downloaded and not keep_zip:
                zipf.unlink()
            raise DownloadError(zipf.name + ' is not a valid zip file.' +
                                ' This may be because exercise does not ' +
                                ' exists or because the download failed')

    assert (cwd / exercise).exists()

    if not keep_zip:
        print('Removing zip file')
        zipf.unlink()

    if cc:
        _download_cpp(exercise)
        return

    if skel_files is None:
        return

    print('Creating skel files')
    if skel_files == -1 or not skel_files:
        skel_files = None
    skel(exercise, skel_files)


def _parse_args(config):
    d = {
        'exercise': config['exercise'],
        'keep_zip': config.getboolean('keep_zip', False),
        'cc': config.getboolean('cc', False),
        #'skel_files': args.skel_files if args.skel else None
        'skel_files': (config['skel_files']
            if config.getboolean('skel') else None)
    }

    def exc():
        return download(**d)
    return exc
