from string import Template
from pathlib import Path
import subprocess
from collections import namedtuple
import shlex
import os
import signal
from .compilef import compilef, make_get_info
from ._aux.errors import TestError, CompileError
from ._aux.config_file import ConfigFile, process_args
from ._aux.print_cmd import print_cmd

# Ugly hack to get signal name from signal code
SIGNALS = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
     if v.startswith('SIG') and not v.startswith('SIG_'))

def test(cases=None, compile=None, diff=True, diff_tool=None,
         verbose=False, make=None, *, config=None):
    args = [
        ('test.compile', compile),
        ('test.diff', diff),
        ('test.diff tool', diff_tool),
        ('compiler.make', make)
    ]
    compile, diff, diff_tool, make = process_args(config, args)
    if diff_tool is None:
        diff_tool = 'diff -y $output $correct'
    diff_tpl = Template(diff_tool)
    cwd = Path.cwd()

    if makefile.exists():
        try:
            executable, outdated = make_get_info(make, makefile)
        except CompileError as ex:
            raise TestError(ex)
    else:
        executable = cwd / (cwd.name.split('_')[0] + '.x')
        outdated = compile or not executable.exists()
    if outdated:
        try:
            compilef(config=config)
        except CompileError as ex:
            raise TestError(ex) from ex
    assert(executable.exists())

    FailedCase = namedtuple('FailedCase', ['case', 'out', 'cor'])
    failed_cases = []

    for inpfile in sorted(cwd.glob('*.inp')):
        corfile = inpfile.with_suffix('.cor')
        try:
            inp = inpfile.open('r')
            out = subprocess.check_output([str(executable)], stdin=inp)
        except subprocess.CalledProcessError as ex:
            if verbose:
                print()
                print('=' * 10)
                print('sample "{}" failed.'.format(inpfile.stem))
                print('Output:')
                print('-' * 10)
            try:
                if verbose:
                    print(out)
                else:
                    out  # Ensure that 'out' is defined
            except NameError:
                if verbose:
                    print('(No output)')
                out = None
            if verbose:
                print('-' * 10)
                print('Further information can be found on the error message')
                print('=' * 10)
            msg = ('sample exited with non-zero status, stopping: '
                + str(ex.returncode))
            try:
                if ex.returncode < 0:
                    msg += (
                        ' (signal ' +
                        SIGNALS.get(-ex.returncode, str(-ex.returncode)) + ')'
                    )
                else:
                    msg += ' (' + os.strerror(ex.returncode) + ')'
            except ValueError:
                pass

            raise TestError(msg, out=out)
        finally:
            inp.close()

        with corfile.open('rb') as corobj:
                cor = corobj.read()
        casename = inpfile.with_suffix('').name
        if out == cor:
            print(casename + ' passed')
        else:
            print(casename + ' failed')
            failed_cases.append(FailedCase(
                case=inpfile.with_suffix('').name,
                out=out, cor=cor
            ))

    if not failed_cases:
        return

    all_output = cwd / '.all_output'
    all_correct = cwd / '.all_correct'
    try:
        out = all_output.open('wb')
        cor = all_correct.open('wb')
        out.write('## OUTPUT ##\n'.encode('utf-8'))
        cor.write('## CORRECT ##\n'.encode('utf-8'))

        for fc in failed_cases:
            out.write('\n# {} #\n'.format(fc.case).encode('utf-8'))
            out.write(fc.out)
            cor.write('\n# {} #\n'.format(fc.case).encode('utf-8'))
            cor.write(fc.cor)
    finally:
        out.close()
        cor.close()

    diff_command = diff_tpl.safe_substitute(
        output=shlex.quote(str(all_output)),
        correct=shlex.quote(str(all_correct))
    )

    print_cmd(diff_command, shell=True)
    subprocess.call(diff_command, shell=True)

    all_output.unlink()
    all_correct.unlink()


def _parse_args(config):
    def exc():
        return test(
            cases=config['_arg.cases'],
            verbose=True,
            config=config
        )
    return exc

def _setup_parser(parent):
    test_parser = parent.add_parser(
        'test', aliases=['t'],
        description='Test the exercise in the current dir and show the diff'
                    ' if a case fails.',
        help='test the current exercise with the test cases'
    )
    test_parser.set_defaults(action=_parse_args)

    test_parser.add_argument(
        ConfigFile.argname('_arg.cases'),
        metavar='case',
        nargs='*',
        help='test only this case(s). By default all cases are tested.'
             ' Specify without extension: `sample1`...'
    )

    compile_group = test_parser.add_mutually_exclusive_group()
    compile_group.add_argument(
        '-c', '--compile',
        action='store_true',
        dest=ConfigFile.argname('test.compile'),
        help='recompile always (ignored with a Makefile) (default)'
    )
    compile_group.add_argument(
        '-C', '--no-compile',
        action='store_false',
        dest=ConfigFile.argname('test.compile'),
        help='do not recompile. Ignored if there is not an executable'
    )
    strict_group = test_parser.add_mutually_exclusive_group()
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

    debug_group = test_parser.add_mutually_exclusive_group()
    debug_group.add_argument(
        '--debug',
        action='store_true',
        dest=ConfigFile.argname('compiler.debug'),
        help='compile with --debug (default)'
    )
    debug_group.add_argument(
        '--no-debug',
        action='store_false',
        dest=ConfigFile.argname('compiler.debug'),
        help='compile with --no-debug (no effect with --no-compile)'
    )

    test_diff_group = test_parser.add_mutually_exclusive_group()
    test_diff_group.add_argument(
        '-D', '--no-diff',
        action='store_false',
        dest=ConfigFile.argname('test.diff'),
        help='do not display a diff when test cases fail'
    )
    test_diff_group.add_argument(
        '-d', '--diff-tool',
        dest=ConfigFile.argname('test.diff tool'),
        help='diff tool to use. "$output" and "$correct" will be substituted '
             ' (they are already quoted).'
             ' Default: `diff -y $output $correct`'
    )

    return test_parser
