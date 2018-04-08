from textwrap import dedent as _dedent

_main_template = '''\
    #include <iostream>

    using namespace std;

    int main() {
        // Code
    }
    '''

_header_template = '''\
    #ifndef {macroname}
    #define {macroname}

    // Code

    #endif // {macroname}
    '''

_source_template = '''\
    #include "{header}"

    // Code
    '''

_source_no_header_template = '''\
    // Code
    '''

def main_template():
    return _dedent(_main_template)

def header_template(macroname):
    return _dedent(_header_template.format(macroname=macroname))

def source_template(header):
    return _dedent(_source_template.format(header=header))

def source_no_header_template():
    return _dedent(_source_no_header_template)
