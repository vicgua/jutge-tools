import pkg_resources
from string import Template

def _get_skel(file):
    return Template(pkg_resources.resource_string(
        __name__, 'data/skel/' + file).decode('utf-8'))

def main_template():
    return _get_skel('main.cc').substitute()

def header_template(macroname):
    return _get_skel('header.hh').substitute(macroname=macroname))

def source_template(header):
    return _get_skel('source.cc').substitute(header=header))

def source_no_header_template():
    return _get_skel('source_no_header.cc').substitute()
