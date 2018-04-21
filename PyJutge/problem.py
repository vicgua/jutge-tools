import attr
import re
import requests
from lxml import html
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
