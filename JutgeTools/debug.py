from string import Template
from pathlib import Path
import subprocess
import shlex
from ._aux.errors import DebugError, CompileError, MakeError
from .compilef import compilef, make_get_info
from ._aux.config_file import ConfigFile, process_args
from ._aux.print_cmd import print_cmd
from ._aux.make import Makefile

def debug(debugger=None, make=None, *, config=None):
    args = [
        ('debugger.cmd', debugger),
        ('compiler.make', make)
    ]
    debugger, make = process_args(config, args)
    debugger_tpl = Template(debugger)
    cwd = Path.cwd()

    if makefile.exists():
        try:
            executable, outdated = make_get_info(make, makefile)
        except CompileError as ex:
            raise DebugError(ex)
    else:
        executable = cwd / (cwd.name.split('_')[0] + '.x')
        outdated = compile or not executable.exists()
    if outdated:
        try:
            compilef(config=config)
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
    def exc():
        return debug(config=config)
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
        metavar='DEBUGGER',
        help='debbugger to be used. "$exe" will be substituted '
             ' (it is already quoted).'
             ' Default: `gdb -tui $exe`'
    )

    strict_group = debug_parser.add_mutually_exclusive_group()
    strict_group.add_argument(
        '--strict',
        action='store_true',
        dest=ConfigFile.argname('compiler.strict'),
        help='compile with the --strict flag'
    )
    strict_group.add_argument(
        '--no-strict',
        action='store_false',
        dest=ConfigFile.argname('compiler.strict'),
        help='compile with the --no-strict flag'
    )

    return debug_parser
