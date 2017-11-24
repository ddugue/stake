import argparse
import importlib
import os
import sys

import logging
LOGGER = logging.getLogger()
HANDLER = logging.StreamHandler()
LOGGER.addHandler(HANDLER)

from .renderer import Renderer
from . import params


def import_element(path):
    "Import and return a single element via importlib"

    packages = path.split(".")
    # if packages[-1][0].isupper(): # Means its a class
    module = ".".join(packages[:-1])
    return getattr(importlib.import_module(module), packages[-1])
    # return getattr(importlib.import_module(path), "__default__")

class Loader:
    "Loads the different modules and renders a file"

    @params.string("config_type", default="stake.config.ini.parser")
    def get_config(self, config_type, **__):
        "Load a specific config type"
        return import_element(config_type)

    @params.array("extensions", short="x", default=[], help="Extensions to load")
    @params.array("extension_dir", default=["."], help="Extension directories to add to sys path relative to project root")
    def get_extensions(self, extensions, extension_dir, **__) -> list:
        "Imports and returns the list of extensions"
        for d in extension_dir:
            sys.path.append(os.path.join(os.getcwd(), d))
        return [import_element(extension) for extension in extensions]

    @params.string("output", short="o", default=None, help="Save render to output (default stdout)")
    @params.string("output_dir", default=".", help="Directory of output for relative paths")
    def get_output(self, output, output_dir, **__):
        "Return a file-like object to output the result of the render"
        if output:
            result_path = os.path.abspath(os.path.join(output_dir, output))
            result_dir = os.path.dirname(result_path)
            os.makedirs(result_dir, exist_ok=True)
            return open(result_path, "w")
        return sys.stdout

    @params.boolean("verbose", default=False, help="Verbose output")
    def configure_logger(self, verbose, **__):
        if verbose:
            LOGGER.setLevel(logging.DEBUG)
        else:
            LOGGER.setLevel(logging.WARNING)

    def __init__(self):
        self.parser = argparse.ArgumentParser(conflict_handler="resolve")
        self.parser.add_argument("file", help="Relative file path")

    def parse_args(self, previous=None):
        "Parse arguments and update them with the new values"
        params.add_arguments(self.parser, previous)

        if not previous:
            previous = {}
        previous.update(vars(self.parser.parse_known_args()[0]))
        return previous

    def __call__(self):
        # Parse crucial values
        values = self.parse_args()

        self.configure_logger(**values)
        config_cls = self.get_config(**values)

        # Reparse values with new parameters added from config
        values = self.parse_args(values)
        values.update(config_cls(**values))

        # Reconfigure logger in case there was some different values in config
        self.configure_logger(**values)

        # Finally load extensions and reparse values
        # based on extensions
        extensions = self.get_extensions(**values)
        values = self.parse_args(values)

        LOGGER.debug("Rendering %s with extensions %s...", values.get("file"), extensions)
        # By decoration, create a composite renderer from the extensions
        # and with the base renderer
        renderable = Renderer(**values)
        while extensions:
            renderable = extensions.pop()(renderable, **values)

        rendered = renderable(values.get("file"))

        LOGGER.debug("Saving %s to %s...", values.get("file"), values.get("output"))
        output = self.get_output(**values)
        output.write(rendered)
        output.close()

def main():
    try:
        Loader()()
    except Exception as e:
        LOGGER.error(e)
        exit(1)

if __name__ == "__main__":
    main()
