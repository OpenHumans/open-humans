import logging

from colors import color


class LocalFormat(logging.Formatter):
    """
    A logging format for local development.
    """

    def format(self, record):
        if record.levelname == "DEBUG":
            record.levelname = color(record.levelname, fg=240)
        elif record.levelname == "INFO":
            record.levelname = color(record.levelname, fg=248)
        elif record.levelname == "WARNING":
            record.levelname = color(record.levelname, fg=220)
        elif record.levelname == "ERROR":
            record.levelname = color(record.levelname, fg=9)

        record.context = color("{0.name}:{0.lineno}".format(record), fg=5)

        return super(LocalFormat, self).format(record)
