import argparse
import params
import importlib
from config.ini import parser as iniconfigparser
from base import Renderer

class Loader():

    def __init__(self, configparser):
        self.configparser = configs

    def get_argparser(self):
        """Create and return a single argument parser"""
        if not self.argparser:
            self.argparser = argparse.ArgumentParser(conflict_handler="resolve")
            self.argparser.add_argument("src", help="Source file to render")
        return params.to_argparser(self.argparser)

    def get_configparser(self):
        return self.configparser

    @param.string("extensions", help="List of extensions", is_cli=False, default=None)
    def get_renderer(self, extensions, **arguments):
        """Returns a callable that takes a file and returns a string"""
        renderers = [Renderer]
        for cls in extensions:
            module = importlib.import_module(cls)
            renderers.append(import cls)

        argparser = self.get_argparser()
        argparser
        pass

    def get_outputter(self):
        """Returns a callable that takes a string and outputs its content"""
        pass

    def __call__(self):
        argparser = self.get_argparser()
        arguments = vars(argparser.parse_known_args()[0])
        arguments = self.configparser(**arguments)
        renderer = self.get_renderer(self, **arguments):
        output = self.get_outputter()
        output(renderer(arguments["src"]))


if __name__ == "__main__":
    arguments = vars(parser.parse_known_args()[0])
    print(arguments)
    update_arguments = configparser(**arguments)
    print(update_arguments)
    mod = importlib.import_module("config.t")
    parser = params.to_argparser(parser)
    arguments = vars(parser.parse_args())
    print(arguments)
