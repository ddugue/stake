import sys
import logging
import colorlog
import textwrap

class CustomFormatter(colorlog.TTYColoredFormatter):
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
LOGGER.addHandler(HANDLER)

# Exports to proxy our global Logger
error    = LOGGER.error
debug    = LOGGER.debug
info     = LOGGER.info
warning  = LOGGER.info
setLevel = LOGGER.setLevel

WARNING  = logging.WARNING
DEBUG    = logging.DEBUG
ERROR    = logging.ERROR
INFO     = logging.INFO

__default__ = LOGGER
