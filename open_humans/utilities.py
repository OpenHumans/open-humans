import io
import os

from ConfigParser import RawConfigParser


def apply_env():
    """
    Read the `.env` file and apply it to os.environ just like using `foreman
    run` would.
    """
    env = '[root]\n' + io.open('.env', 'r').read()

    config = RawConfigParser(allow_no_value=True)

    # Use `str` instead of the regular option transform to preserve option case
    config.optionxform = str
    config.readfp(io.StringIO(env), '.env')

    os.environ.update(config.items('root'))
