import io
import os

from ConfigParser import RawConfigParser


class EnvParser(RawConfigParser):
    """
    A RawConfigParser that doesn't care about quotes in the same way that
    foreman doesn't care about quotes.
    """
    def get(self, section, option):
        return RawConfigParser.get(self, section, option).strip('"')

    # Don't change the option string at all
    def optionxform(self, option_string):
        return option_string

    def items(self, section):
        return tuple((item, self.get(section, item))
                     for item, _ in RawConfigParser.items(self, section))


def get_env():
    """
    Read the `.env` file and return it.
    """
    try:
        env = '[root]\n' + io.open('.env', 'r').read()
    except IOError:
        return

    config = EnvParser(allow_no_value=True)

    config.readfp(io.StringIO(env), '.env')

    return config.items('root')


def apply_env(env):
    """
    Apply the given env to os.environ just like using `foreman run` would.
    """
    os.environ.update(env)
