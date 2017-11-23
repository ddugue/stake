import argparse
import importlib
import os
import sys
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
    def get_extensions(self, extensions, extension_dir, **__):
        "Imports and returns the list of extensions"
        for d in extension_dir:
            sys.path.append(os.path.join(os.getcwd(), d))
        return [import_element(extension) for extension in extensions]

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

        config_cls = self.get_config(**values)

        # Reparse values with new parameters added from config
        values = self.parse_args(values)
        values.update(config_cls(**values))

        # Finally load extensions and reparse values
        # based on extensions
        extensions = self.get_extensions(**values)
        values = self.parse_args(values)

        print("Extensions: ", extensions)
        # By decoration, create a composite renderer from the extensions
        # and with the base renderer
        renderable = Renderer(**values)
        while extensions:
            renderable = extensions.pop()(renderable, **values)

        print("Context: ", values)
        return renderable(values.get("file"))

def main():
    print(Loader()())

if __name__ == "__main__":
    main()
