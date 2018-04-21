import attr
import re
import requests
import tempfile
from lxml import html
from tarfile import TarFile, TarError
from zipfile import ZipFile, BadZipFile
from ._aux import download


@attr.s
class Problem:
    problem_num = attr.ib(type=str)

    @problem_num.validator
    def check(self, attribute, value):
        if not re.match(r'[PXGQ]\d+_[a-z]+', value):
            raise ValueError(value + ' is not a valid problem name')
        elif value[0] not in 'PX':
            raise ValueError(
                value + ' problem is not compatible with '
                'PyJutge (only P* and X* supported)'
            )

    _problem_properties = attr.ib(
        type=dict, default=None, repr=False, init=False
    )

    @property
    def public(self):
        return self.problem_num[0] != 'X'

    def _get_properties(self):
        url = "https://jutge.org/problems/{}".format(self.problem_num)
        r = requests.get(url)
        r.raise_for_status()
        tree = html.fromstring(r.content)
        zip_url = '/problems/' + self.problem_num + '/zip'
        has_zip = bool(tree.xpath('//a[@href="{}"]'.format(zip_url)))
        cc_url = '/problems/' + self.problem_num + '/main/cc'
        has_cc = bool(tree.xpath('//a[@href="{}"]'.format(cc_url)))
        tar_url = '/problems/' + self.problem_num + '/public.tar'
        has_tar = bool(tree.xpath('//a[@href="{}"]'.format(tar_url)))
        self._problem_properties = {
            'has_zip': has_zip,
            'has_cc': has_cc,
            'has_tar': has_tar
        }

    def has_zip(self):
        if not self._problem_properties:
            self._get_properties()
        return self._problem_properties['has_zip']

    def has_cc(self):
        if not self._problem_properties:
            self._get_properties()
        return self._problem_properties['has_cc']

    def has_public_tar(self):
        if not self._problem_properties:
            self._get_properties()
        return self._problem_properties['has_tar']

    def download_zip(self, dest, verbose=False):
        url = "https://jutge.org/problems/{}/zip".format(self.problem_num)
        download(url, dest, verbose=verbose)

    def download_cc(self, dest, verbose=False):
        url = "https://jutge.org/problems/{}/main/cc".format(self.problem_num)
        download(url, dest, verbose=verbose)

    def download_public_tar(self, dest, verbose=False):
        url = "https://jutge.org/problems/{}/public.tar".format(
            self.problem_num
        )
        download(url, dest, verbose=verbose)

    def extract_zip(self, dest, verbose=False, tempdest=None):
        """Download and extract the problem zip.
            dest: A Path object pointing to a dir, where a directory with the
                problem name will be created.
            verbose: whether to print progress
            tempdest: Path object pointing to where the zip should be
                downloaded (if it doesn't exist). If None, it will be downloaded
                to a temporal file and deleted afterwards.
            Returns: A Path object pointing to the extracted dir.
        """
        if tempdest is None:
            dldest = tempfile.TemporaryFile('w+b')
            skip_download = False
        elif tempdest.exists():
            dldest = tempdest.open('rb')
            skip_download = True
        else:
            dldest = tempdest.open('w+b')
            skip_download = False

        try:
            if not skip_download:
                self.download_zip(dldest, verbose=verbose)
            if verbose:
                print('Extracting exercise')
            with ZipFile(dldest, 'r') as zipf:
                # TODO: Ensure we don't overwrite existing files
                zipf.extractall(str(dest))
                # While extracting zipfiles could create files in places
                # other than the expected dir (see docs for extractall),
                # I consider these files trusted.
        finally:
            dldest.close()
        problem_dir = dest / self.problem_num
        assert problem_dir.exists()
        return problem_dir

    def extract_public_tar(self, dest, verbose=False, tempdest=None):
        """Download and extract the problem tar.
            dest: A Path object pointing to a dir, where the files in the tar
                file will be extracted.
            verbose: whether to print progress
            tempdest: Path object pointing to where the tar should be
                downloaded (if it doesn't exist). If None, it will be downloaded
                to a temporal file and deleted afterwards.
        """
        if tempdest is None:
            dldest = tempfile.TemporaryFile('w+b')
            skip_download = False
        elif tempdest.exists():
            dldest = tempdest.open('rb')
            skip_download = True
        else:
            dldest = tempdest.open('w+b')
            skip_download = False

        try:
            if not skip_download:
                self.download_public_tar(dldest, verbose=verbose)
            if verbose:
                print('Extracting public files')
            with TarFile('r', fileobj=dldest) as tarf:
                # TODO: Ensure we don't overwrite existing files
                tarf.extractall(str(dest))
                # See note in extract_zip above
        finally:
            dldest.close()
