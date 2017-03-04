import configparser

from . import base
from utils import *
import params

@params.string("config", help="Relative path to the config file")
def parser(config, **arguments):
    return arguments
    # parser = configparser.ConfigParser(dict_type=dict)
    # parser.read(self.config)
    # values = {s:dict(parser.items(s)) for s in parser.sections()}
    # return values
