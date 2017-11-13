import configparser
from collections.abc import MutableMapping
from pathlib import Path

class ConfigFile(MutableMapping):
    def __init__(self, args):
        self.override = args
        self.config = configparser.ConfigParser()
        self.file = None
        if args.config is not None:
            self.config.read(args.config)
            self.file = Path(args.config)
            if not self.file.exists():
                self.save()
            self.file = self.file.resolve()

    def __getitem__(self, key):
        ret = getattr(self.override, key, None)
        if ret is None:
            ret = self.config['DEFAULT'][key]
        return ret

    def __setitem__(self, key, value):
        setattr(self.override, key, value)
        self.config['DEFAULT'][key] = str(value)

    def __delitem__(self, key):
        delattr(self.override, key)
        del self.config['DEFAULT'][key]

    def __iter__(self):
        for f in self.override:
            yield f
        for c in self.config:
            yield c

    def __len__(self):
        return max(len(self.override, self.config))

    def get(self, key, fallback=None):
        ret = getattr(self.override, key, None)
        if ret is None:
            ret = self.config.get('DEFAULT', key, fallback=fallback)
        return ret

    def getint(self, key, fallback=None):
        ret = getattr(self.override, key, None)
        if ret is None:
            ret = self.config.getint('DEFAULT', key, fallback=fallback)
        return ret

    def getfloat(self, key, fallback=None):
        ret = getattr(self.override, key, None)
        if ret is None:
            ret = self.config.getfloat('DEFAULT', key, fallback=fallback)
        return ret

    def getboolean(self, key, fallback=None):
        ret = getattr(self.override, key, None)
        if ret is None:
            ret = self.config.getboolean('DEFAULT', key, fallback=fallback)
        return ret

    def save(self):
        if self.file is not None:
            with self.file.open('w') as cfg:
                self.config.write(cfg)
