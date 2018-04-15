import subprocess
import os
from pathlib import Path
from .print_cmd import print_cmd
from .errors import MakeError

class Makefile:
    def __init__(self, make_path, makefile):
        self.make_path = make_path
        self.makefile = makefile
        assert(makefile.name == 'Makefile')

    def make_target(self, target, env=None, verbose=False):
        if target is None:
            cmd = [self.make_path]
        else:
            cmd = [self.make_path, target]
        if verbose:
            print_cmd(cmd, env=env)
        if env:
            # new_env = {**os.environ, **env}  # (Python >= 3.5)
            new_env = dict(os.environ, **env)
            proc = subprocess.Popen(cmd, cwd=self.makefile.parent, env=new_env)
        else:
            proc = subprocess.Popen(cmd, cwd=self.makefile.parent)
        proc.wait()
        if proc.returncode != 0
            raise MakeError(returncode=proc.returncode)

    def make_all(self, env=None, verbose=False):
        return self.make_target(None, env=env, verbose=verbose)

    def executable_name(self):
        cmd = [self.make_path, '_exe_name']
        try:
            return Path(subprocess.check_output(cmd, universal_newlines=True))
        except subprocess.CalledProcessError as ex:
            raise MakeError(returncode=ex.returncode)

    def outdated(self):
        cmd = [self.make_path, '--question']
        ret = subprocess.call(cmd)
        return ret != 0
