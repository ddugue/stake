import argparse
import importlib
from renderer import Renderer
import params

def import_element(path):
    "Import and return a single element via importlib"

    packages = path.split(".")
    if packages[-1][0].isupper(): # Means its a class
        module = ".".join(packages[:-1])
        return getattr(importlib.import_module(module), packages[-1])
    return getattr(importlib.import_module(path), "__default__")


class Loader:
    "Loads the different modules and renders a file"

    @params.string("config_type", default="config.ini.parser")
    def get_config(self, config_type, **__):
        "Load a specific config type"
        return import_element(config_type)

    @params.array("extensions", short="x", default=[])
    def get_extensions(self, extensions, **__):
        "Imports and returns the list of extensions"
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
        values = self.parse_args()

        config_cls = self.get_config(**values)

        values = self.parse_args(values)
        values.update(config_cls(**values))

        extensions = self.get_extensions(**values)
        values = self.parse_args(values)

        renderable = Renderer(**values)
        while extensions:
            renderable = extensions.pop()(renderable, **values)

        return renderable(values.get("file"))

if __name__ == "__main__":
    print(Loader()())
