class ProcessError(Exception):
    pass

class DownloadError(ProcessError):
    pass

class CompileError(ProcessError):
    pass

class TestError(ProcessError):
    def __init__(self, *args, out=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.out = out

class DebugError(ProcessError):
    pass

class SkelError(ProcessError):
    pass
