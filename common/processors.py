import re
import six

from env_tools import load_env

from raven.processors import Processor
from raven.utils import varmap


class SanitizeEnvProcessor(Processor):
    """
    Sanitize the environment to prevent leaking data like credit cards and
    passwords.
    """
    MASK = '*' * 8
    FIELDS = []

    env = load_env()

    if env:
        FIELDS = [k for k, _ in env]

    VALUES_RE = re.compile(r'^(?:\d[ -]*?){13,16}$')

    def sanitize(self, key, value):
        if value is None:
            return

        if not key:  # key can be a NoneType
            return value

        key = key.lower()

        for field in self.FIELDS:
            if field in key:
                # store mask as a fixed length for security
                return self.MASK

        return value

    def filter_stacktrace(self, data):
        for frame in data.get('frames', []):
            if 'vars' not in frame:
                continue

            frame['vars'] = varmap(self.sanitize, frame['vars'])

    def filter_http(self, data):
        for n in ('data', 'cookies', 'headers', 'env', 'query_string'):
            if n not in data:
                continue

            if isinstance(data[n], six.string_types) and '=' in data[n]:
                # at this point we've assumed it's a standard HTTP query
                querybits = []

                for bit in data[n].split('&'):
                    chunk = bit.split('=')
                    if len(chunk) == 2:
                        querybits.append((chunk[0], self.sanitize(*chunk)))
                    else:
                        querybits.append(chunk)

                data[n] = '&'.join('='.join(k) for k in querybits)
            else:
                data[n] = varmap(self.sanitize, data[n])
