import warnings

warnings.warn('genconfig is deprecated. Use the new module "config" instead',
              DeprecationWarning)

def genconfig(config, compiler, diff_tool, debugger):
    if compiler:
        config['compiler'] = compiler
    else:
        config['compiler'] = 'g++ -o $output $flags $sources'

    if diff_tool:
        config['diff_tool'] = diff_tool
    else:
        config['diff_tool'] = 'diff -y $output $correct'

    if debugger:
        config['debugger'] = debugger
    else:
        config['debugger'] = 'gdb -tui $exe'
    config.save()

def _parse_args(config):
    d = {
        'compiler': config.get('compiler'),
        'diff_tool': config.get('diff_tool'),
        'debugger': config.get('debugger')
    }

    def exc():
        return genconfig(config, **d)
    return exc

def _setup_parser(parent):
    genconfig_parser = parent.add_parser(
        'genconfig',
        description='Generate or update a config file and write it to'
                    ' the location specified by --config',
        help='generate or update a config file'
    )
    genconfig_parser.add_argument(
        '-c', '--compiler',
        help='compiler to be used. "$sources" and "$flags" will be substituted'
             ' (they are already quoted). "$flags" are g++-style flags'
    )
    genconfig_parser.add_argument(
        '-diff', '--diff-tool',
        help='diff tool to use. "$output" and "$correct" will be substituted'
             ' (they are already quoted)'
    )
    genconfig_parser.add_argument(
        '-dbg', '--debugger',
        help='debbugger to be used. "$exe" will be substituted'
             ' (it is already quoted)'
    )
    genconfig_parser.set_defaults(action=_parse_args)

    return genconfig_parser
