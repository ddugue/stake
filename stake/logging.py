import sys
import logging
import colorlog
import textwrap

class CustomFormatter(colorlog.ColoredFormatter):
    """ Colored formatter that removes indentation caused by triple quotes """
    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = textwrap.dedent(record.msg)
        return super().format(record)

# Configure Logger
LOGGER = colorlog.getLogger()
HANDLER = colorlog.StreamHandler(sys.stdout)
HANDLER.setFormatter(CustomFormatter(
	'%(log_color)s[%(levelname)s]: %(message)s'))
HANDLER.addFilter(lambda record: record.levelno != logging.ERROR)

ERROR_HANDLER = colorlog.StreamHandler(sys.stderr)
ERROR_HANDLER.setFormatter(CustomFormatter(
	'%(log_color)s[%(levelname)s]: %(message)s'))
ERROR_HANDLER.addFilter(lambda record: record.levelno == logging.ERROR)

LOGGER.addHandler(HANDLER)
LOGGER.addHandler(ERROR_HANDLER)

# Exports to proxy our global Logger
error    = LOGGER.error
debug    = LOGGER.debug
info     = LOGGER.info
warning  = LOGGER.warning
setLevel = LOGGER.setLevel

WARNING  = logging.WARNING
DEBUG    = logging.DEBUG
ERROR    = logging.ERROR
INFO     = logging.INFO

__default__ = LOGGER
