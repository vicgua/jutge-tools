from ._aux.config_file import ConfigFile
from ._aux.errors import ConfigError

SUBACTION_NAME = ConfigFile.argname('_arg.subaction')


def init_config(config):
    config.save()


def show_config(config):
    settings = config['_arg.settings']
    max_len = max(map(len, settings))
    for s in settings:
        try:
            value = config[s]
            if value is None:
                raise KeyError
        except KeyError:
            print('{s:>{l}}: No value set'.format(s=s, l=max_len))
        else:
            print('{s:{l}} = {v}'.format(s=s, l=max_len, v=value))


def set_config(config):
    setting = config['_arg.setting']
    unset = config['_arg.unset']
    if unset:
        del config[setting]
    else:
        values = config['_arg.values']
        try:
            if len(values) == 1:
                config[setting], typecast_ok = (
                    ConfigFile.autoconvert(setting, values[0])
                )
            else:
                config[setting], typecast_ok = (
                    ConfigFile.autoconvert(setting, values)
                )
            assert typecast_ok
        except TypeError as err:
            raise ConfigError(err)
    config.save()


def _parse_args(config):
    return lambda: {
        'init': init_config,
        'show': show_config,
        'set': set_config
    }[config[SUBACTION_NAME]](config)
    # Redirect to the function acording to the subaction


def _setup_parser(parent):
    config_parser = parent.add_parser(
        'config',
        description='Generate, update or show the config file',
        help='generate, update or show the config file'
    )

    subparsers = config_parser.add_subparsers()

    init_subparser = subparsers.add_parser(
        'init',
        help="generate the config file. If it already exists, it won't be"
        " changed"
    )
    init_subparser.set_defaults(**{SUBACTION_NAME: 'init'})
    # This is required so that the subaction gets through to _parse_args

    show_subparser = subparsers.add_parser(
        'show', help='show config file settings'
    )
    show_subparser.add_argument(
        ConfigFile.argname('_arg.settings'),
        metavar='setting',
        nargs='+',
        help='setting(s) that you want to show'
    )
    show_subparser.set_defaults(**{SUBACTION_NAME: 'show'})

    set_subparser = subparsers.add_parser(
        'set', help='set a config file setting'
    )
    set_subparser.add_argument(
        ConfigFile.argname('_arg.setting'),
        metavar='setting',
        help='setting to be modified'
    )
    set_subparser.add_argument(
        ConfigFile.argname('_arg.values'),
        metavar='value',
        nargs='*',
        help='new value of (setting). If more than one value is provided, a '
        'list will be created. For boolean variables, {1, true, yes, t,'
        ' y} are considered True, and {0, false, no, f, n} are False. If'
        ' --unset, this argument is ignored.'
    )
    set_subparser.add_argument(
        '-u',
        '--unset',
        action='store_true',
        default=False,
        dest=ConfigFile.argname('_arg.unset'),
        help='delete the variable (the default value, if any,'
        ' will be used instead)'
    )
    set_subparser.set_defaults(**{SUBACTION_NAME: 'set'})

    config_parser.set_defaults(action=_parse_args)

    return config_parser
