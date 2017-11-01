from string import Template
from pathlib import Path
import subprocess
import shlex
from ._aux.errors import DebugError, CompileError
from .compilef import compilef

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

    try:
        debugger_cmd = debugger_tpl.substitute(
            exe=shlex.quote(str(executable))
        )
    except KeyError as ex:
        raise DebugError('{} is not a valid variable'.format(ex))
    print('Starting debugger')
    subprocess.call(debugger_cmd, shell=True)

def _parse_args(args):
    d = {
        'debugger': args.debugger,
        'strict': args.strict
    }

    def exc():
        return debug(**d)
    return exc