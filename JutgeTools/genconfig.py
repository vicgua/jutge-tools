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
