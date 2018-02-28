import yaml
from pathlib import Path

# TODO: For boolean variables, flags with both --x and --no-x should be set
# Otherwise, if the user defined a value other than the default, it will
# always be used
CONFIG_VARIABLES = {
    # cfgpath: (type, argname (None to use default), default value)
    # argname is required if the cfgpath contains something other that
    # valid Python identifiers, ., - and space.

    # compiler
    'compiler.cmd': (str, None, 'g++ -o $output $flags $sources'),
    'compiler.debug': (bool, None, True),
    'compiler.strict': (bool, None, True),

    # debugger
    'debugger.cmd': (str, None, 'gdb -tui $exe'),

    # download
    'download.keep zip': (bool, None, False),
    'download.skel': (bool, None, True),
    'download.skel files': (list, None, list),  # If using a callable, it will
    # be called to build the default value

    # shrc
    'shrc.p1++ alias': (bool, 'p1_alias', True),
    # TODO: Change to allow name customization
    # 'shrc.p2++ alias': (bool, 'p2_alias', True)  # TODO
    'shrc.dl alias': (str, None, 'dl'),

    # test
    'test.compile': (bool, None, True),
    'test.diff': (bool, None, True),
    'test.diff tool': (str, None, 'diff -y $output $correct')
}

class ConfigFile:
    def __init__(self, args):
        self.override = args
        self.config = self.build_default_config()
        self.file = None
        if args.config is not None:
            # An explicit config file has been set
            self.file = Path(args.config).expanduser()
        else:
            # Use a default path for config file
            self.file = Path('~/.jutge-tools.yml').expanduser()
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

    @staticmethod
    def argname(cfgpath):
        '''Get the argument name from the config path.

        For example: a.b-c.d -> a__b_c__d
        '''
        try:
            set_argname = CONFIG_VARIABLES[cfgpath][1]
            if set_argname is not None:
                return set_argname
        except KeyError:
            # Non-standard key. Use the usual method
            pass
        transtable = str.maketrans({'.': '__', '-': '_', ' ': '_'})
        return cfgpath.translate(transtable)

    def __getitem__(self, key):
        ret = getattr(self.override, self.argname(key), None)
        if ret is None:
            ret = self.cfgpath_get(self.config, key.split('.'))
        try:
            converter, _, default = CONFIG_VARIABLES[key]
        except KeyError:
            return ret  # "key" is not a standard key
        if ret is None:
            if callable(default):
                # For lists
                return default()
            return default
        return converter(ret)

    @staticmethod
    def autoconvert(key, value):
        if value is None:
            return value, True
        try:
            required_type = CONFIG_VARIABLES[key][0]
        except KeyError:
            return value, True
        if isinstance(value, required_type):
            return value, True
        try:
            if required_type is list:
                return [value], True
            if required_type is bool and isinstance(value, str):
                TRUTHY_VALUES = {'1', 'true', 'yes', 't', 'y'}
                FALSEY_VALUES = {'0', 'false', 'no', 'f', 'n'}
                if value.lower() in TRUTHY_VALUES:
                    return True, True
                elif value.lower() in FALSEY_VALUES:
                    return False, True
                else:
                    return value, False
            return required_type(value), True
        except:
            return value, False  # Failed

    def __setitem__(self, key, value):
        try:
            required_type = CONFIG_VARIABLES[key][0]
        except KeyError:
            pass  # Non-standard config variables always type-check
        else:
            # Type checking for standard config variables
            if value is not None and not isinstance(value, required_type):
                raise TypeError(
                    'config value {} must be a {} ({} passed)'.format(
                        key,
                        required_type.__qualname__,
                        type(value).__qualname__
                    ))
        # Add an override in case there is one already (another option
        # would be to delete the override)
        setattr(self.override, self.argname(key), value)
        # Set it in the permanent config, so it will be saved with save()
        self.cfgpath_set(self.config, key.split('.'), value)

    def __delitem__(self, key):
        try:
            delattr(self.override, self.argname(key))
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
            yaml.dump(self.config, f, default_flow_style=False)
