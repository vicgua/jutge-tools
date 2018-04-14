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

    # TODO: Factor this into its own function (repeated in .test)
    makefile = cwd / 'Makefile'
    if makefile.exists():
        try:
            executable = Path(subprocess.check_output(['make', '_exe_name'],
                universal_newlines=True))
        except subprocess.CalledProcessError as ex:
            raise TestError('could not determine the executable name:'
                            " 'make _exe_name' exited with status {}."
                            ' Maybe not a JutgeTools Makefile?')
        outdated = subprocess.run(['make', '--question']).returncode != 0
    else:
        executable = cwd / (cwd.name.split('_')[0] + '.x')
        outdated = compile or not executable.exists()
    if outdated:
        try:
            compilef(strict=strict, debug=debug)
        except CompileError as ex:
            raise TestError(ex) from ex
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
