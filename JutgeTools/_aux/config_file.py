import yaml
from pathlib import Path

CONFIG_VARIABLES = {
    'tools.compiler': (str, 'g++ -o $output $flags $sources'),
    'tools.diff-tool': (str, 'diff -y $output $correct'),
    'tools.debugger': (str, 'gdb -tui $exe')
}

class ConfigFile:
    def __init__(self, args):
        self.override = args
        self.config = self.build_default_config()
        self.file = None
        if args.config is not None:
            # An explicit config file has been set
            self.file = Path(args.config).expanduser().resolve()
        else:
            # Use a default path for config file
            self.file = Path('~/.jutge-tools.yml').expanduser().resolve()
        try:
            with self.file.open('r') as f:
                self.config.update(yaml.safe_load(f))
        except OSError:
            # File could not be read. The default config will be used
            # and saved (if possible)
            pass

        self.save()  # Dump the current config. This will remove comments,
        # but keep the file up-to-date.

    @staticmethod
    def cfgpath_get(cfgdict, cfgpath):
        '''Get a value from a config path

        cfgpath must be an iterable. If we wanted to get path 'a.b.c', cfgpath
        would be ['a', 'b', 'c']
        '''
        celem, *restpath = cfgpath
        if not restpath:
            # This is the last path element
            return cfgdict[celem]
        return ConfigFile.cfgpath_get(cfgdict[celem], restpath)

    @staticmethod
    def cfgpath_set(cfgdict, cfgpath, value):
        '''Set a value from a config path

        cfgpath must be an iterable. If we wanted to set path 'a.b.c', cfgpath
        would be ['a', 'b', 'c']
        '''
        celem, *restpath = cfgpath
        if not restpath:
            # This is the last path element
            cfgdict[celem] = value
        else:
            newdict = cfgdict.setdefault(celem, {})
            # If cfgdict[celem] already exists, get that; else, insert a new {}
            ConfigFile.cfgpath_set(newdict, restpath, value)

    @staticmethod
    def cfgpath_del(cfgdict, cfgpath):
        '''Delete a value from a config path

        cfgpath must be an iterable. If we wanted to delete path 'a.b.c',
        cfgpath would be ['a', 'b', 'c']
        '''
        celem, *restpath = cfgpath
        if not restpath:
            # This is the last path element
            del cfgdict[celem]
        else:
            ConfigFile.cfgpath_del(cfgdict[celem], restpath)
            if not cfgdict[celem]:
                # This path node is now empty and may be deleted
                del cfgdict[celem]

    @staticmethod
    def build_default_config():
        config = {}
        for var in CONFIG_VARIABLES:
            ConfigFile.cfgpath_set(config, var.split('.'), None)
        return config

    def __getitem__(self, key):
        ret = getattr(self.override, key.replace('.', '__'), None)
        # TODO: Change override keys so that they match the key,
        # replacing '.' with '__' ('a.b.c' -> 'a__b__c')
        if ret is None:
            ret = self.cfgpath_get(self.config, key.split('.'))
        try:
            converter, default = CONFIG_VARIABLES[key]
        except KeyError:
            return ret  # "key" is not a standard key
        if ret is None:
            return default
        return converter(ret)

    def __setitem__(self, key, value):
        try:
            required_type = CONFIG_VARIABLES[key]
        except KeyError:
            pass  # Non-standard config variables always type-check
        else:
            # Type checking for standard config variables
            if not isinstance(value, required_type):
                raise TypeError(
                    'config value {} must be a {} ({} passed)'.format(
                        key,
                        required_type.__qualname__,
                        type(value).__qualname__
                    ))
        # Add an override in case there is one already (another option
        # would be to delete the override)
        setattr(self.override, key.replace('.', '__'), value)
        # Set it in the permanent config, so it will be saved with save()
        self.cfgpath_set(self.config, key.split('.'), value)

    def __delitem__(self, key):
        try:
            delattr(self.override, key.replace('.', '__'))
        except AttributeError:
            pass  # The key has no override
        if key in CONFIG_VARIABLES:
            self.cfgpath_set(self.config, key.split('.'), None)  # Set to None
            # to use default value
        else:
            # Key not recognised, and may be deleted (instead of set to None)
            self.cfgpath_del(self.config, key.split('.'))



    def save(self):
        with self.file.open('w') as f:
            yaml.dump(self.config, f)
