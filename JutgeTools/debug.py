from string import Template
from pathlib import Path
import subprocess
import shlex
from ._aux.errors import DebugError, CompileError
from .compilef import compilef
from ._aux.config_file import ConfigFile
from ._aux.print_cmd import print_cmd

# TODO: Avoid passing arguments to compiler, use instead config
def debug(debugger=None, compile=True, strict=True):
    if debugger is None:
        debugger = 'gdb -tui $exe'  # GDB with GUI
    debugger_tpl = Template(debugger)
    cwd = Path.cwd()

    executable = cwd / (cwd.name.split('_')[0] + '.x')
    if compile or not executable.exists():
        try:
            compilef(strict=strict)
        except CompileError as ex:
            raise DebugError(ex) from ex
    assert(executable.exists())

    debugger_cmd = debugger_tpl.safe_substitute(
        exe=shlex.quote(str(executable))
    )
    print('Starting debugger')
    print_cmd(debugger_cmd, shell=True)
    subprocess.call(debugger_cmd, shell=True)

def _parse_args(config):
    d = {
        'debugger': config['debugger.cmd'],
        'strict': config['compiler.strict']
    }

    def exc():
        return debug(**d)
    return exc

def _setup_parser(parent):
    debug_parser = parent.add_parser(
        'debug', aliases=['dbg'],
        description='Start a debugger attached to the executable',
        help='run on a debugger'
    )
    debug_parser.set_defaults(action=_parse_args)

    debug_parser.add_argument(
        '-d', '--debugger',
        dest=ConfigFile.argname('debugger.cmd'),
        help='debbugger to be used. "$exe" will be substituted '
             ' (it is already quoted).'
             ' Default: `gdb -tui $exe`'
    )

    debug_parser.add_argument(
        '--no-strict',
        action='store_false',
        dest=ConfigFile.argname('compiler.strict'),
        help='compile with the --no-strict flag'
    )

    return debug_parser
