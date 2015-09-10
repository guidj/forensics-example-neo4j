import os
import os.path
import configparser

PROJECT_BASE = ''.join([os.path.dirname(os.path.abspath(__file__)), "/../../../"])
CONFIG_FILE = ''.join([PROJECT_BASE, 'config.ini'])

_UNSET = object()


class ConfigurationError(Exception):
    pass


def get(section, option=None, type=None, fallback=_UNSET):
    config = configparser.ConfigParser()

    with open(CONFIG_FILE, "r") as fp:
        config.read_file(fp)

        try:

            if option:

                if type:

                    if type in [str, int, float, complex]:
                        value = type(config.get(section, option))

                    elif type == bool:
                        value = config.getboolean(section, option)
                    else:
                        raise ConfigurationError(
                            '{0} is an invalid data type. `type` must be a basic data type: '
                            'str, bool, int, float or complex'.format(
                                str(type)
                            )
                        )
                else:

                    value = config.get(section, option)

                return value

            else:

                data = dict(config.items(section))

                return data

        except (configparser.NoOptionError, configparser.NoSectionError) as exc:

            if fallback is _UNSET:
                raise ConfigurationError(exc)
            else:
                return fallback


def save(section, option, value):
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as fp:
            config.read_file(fp)

    with open(CONFIG_FILE, "w") as fp:

        try:

            if config.has_section(section) is False:
                config.add_section(section)

            config.set(section, option, str(value))

            config.write(fp)
        except configparser.Error as exc:
            raise ConfigurationError(exc)
