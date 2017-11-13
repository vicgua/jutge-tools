from string import Template
from pathlib import Path
import subprocess
from collections import namedtuple
import shlex
from .compilef import compilef
from ._aux.errors import TestError, CompileError

def test(cases=None, compile=True, strict=True, debug=True, diff=True,
         diff_tool=None):
    if diff_tool is None:
        diff_tool = 'diff -y $output $correct'
    diff_tpl = Template(diff_tool)
    cwd = Path.cwd()

    executable = cwd / (cwd.name.split('_')[0] + '.x')
    if compile or not executable.exists():
        try:
            compilef(strict=strict, debug=debug)
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
        except subprocess.CalledProcessError as ex:
            raise TestError('sample exited with non-zero status, stopping: '
                            + str(ex.returncode))
        finally:
            inp.close()

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

    try:
        diff_command = diff_tpl.substitute(
            output=shlex.quote(str(all_output)),
            correct=shlex.quote(str(all_correct))
        )
    except KeyError as ex:
        raise TestError('{} is not a valid variable'.format(ex))

    print('> ' + diff_command)
    subprocess.call(diff_command, shell=True)

    all_output.unlink()
    all_correct.unlink()


def _parse_args(config):
    d = {
        'cases': config['case'],
        'compile': config.getboolean('compile', True),
        'strict': config.getboolean('strict', True),
        'debug': config.getboolean('debug', True),
        'diff': config.getboolean('diff', True),
        'diff_tool': config.get('diff_tool')
    }

    def exc():
        return test(**d)
    return exc
