from urllib.request import urlopen
from urllib.error import HTTPError
from pathlib import Path
from zipfile import ZipFile, BadZipfile
from textwrap import dedent
from .errors import DownloadError

template = '''\
    #include <iostream>

    using namespace std;

    int main() {
        // Code
    }
    '''

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


def download(exercise, keep_zip=False, stub_files=-1):
    if stub_files == -1 or stub_files == []:
        stub_files = [exercise.split('_')[0] + '.cc']

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
    
    if stub_files is None:
        return

    print('Creating stub files')
    for s in stub_files:
        s_path = cwd / exercise / s
        s_path.write_text(dedent(template))


def _parse_args(args):
    d = {
        'exercise': args.exercise,
        'keep_zip': args.keep_zip,
        'stub_files': args.stub_file if args.stub else None
    }

    def exc():
        return download(**d)
    return exc