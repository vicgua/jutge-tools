class ProcessError(Exception):
    pass

class DownloadError(ProcessError):
    pass

class CompileError(ProcessError):
    pass

class TestError(ProcessError):
    pass

class DebugError(ProcessError):
    pass

class SkelError(ProcessError):
    pass