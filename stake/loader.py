import argparse
import importlib
import os
import sys

from . import logging
from .renderer import Renderer
from . import params
from .extensions.base import Extension


def import_element(path):
    "Import and return a single element via importlib"
    exception = None

    packages = path.split(".")
    cls = packages[-1] if packages[-1][0].isupper() else None

    module_path = ".".join(packages[:-1]) if cls else path
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        exception = e
        #We shall retry to import module with prepending our own extensions
        try:
            module = importlib.import_module("stake.extensions."+module_path)
        except ModuleNotFoundError as er:
            raise exception
    if cls:
        return getattr(module, cls)
    return getattr(module, "__default__")


class Loader:
    "Loads the different modules and renders a file with Jinja2"

    @params.string("config_file", short="c", help="Relative path to the config file")
    def get_config(self, config_file, **__):
        "Load a specific config type"
        if config_file.endswith("ini"):
            from stake.config.ini import parser
            return parser
        return None

    @params.array("extensions", short="x", default=[], help="Extensions to load")
    @params.array("extension_dir", default=["."], help="Extension directories to add to sys path relative to project root")
    def get_extensions(self, extensions, extension_dir, **__) -> list:
        "Imports and returns the list of extensions"
        for d in extension_dir:
            sys.path.append(os.path.join(os.getcwd(), d))

        for extension in extensions:
            try:
                extension_cls = import_element(extension.strip())
                assert issubclass(extension_cls, Extension)
                yield extension_cls
            except AttributeError as e:
                logging.error("""
                Could not find %s class. Make sure that class %s is in your path.
                To add a directory to your path easily. Simply add a directory in 'extension_dir' parameter.
                """, extension, extension)
                raise e
            except ModuleNotFoundError as e:
                logging.error("""
                Module %s was not found in your path.
                """, extension)
                raise
            except AssertionError as e:
                logging.error("""
                Make sure that %s is extending the base class Extension.
                '''
                from stake.extension.base import Extension
                class YourClass(Extension):
                    ...

                '''""", extension)
                raise e

    @params.string("output", short="o", default=None, help="Save render to OUTPUT (default stdout)")
    @params.string("output_dir", default=".", help="Directory of OUTPUT for relative paths")
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
        "Configure the global logger based on arguments parsed by the Loader"
        if verbose:
            logging.setLevel(logging.DEBUG)
        else:
            logging.setLevel(logging.WARNING)

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
        extensions = list(self.get_extensions(**values))
        logging.debug("Reparsing CLI arguments with new extensions loaded...")
        values = self.parse_args(values)

        logging.debug("Rendering %s with extensions %s...", values.get("file"), extensions)
        # By decoration, create a composite renderer from the extensions
        # and with the base renderer
        renderable = Renderer(**values)
        while extensions:
            renderable = extensions.pop()(renderable, **values)

        rendered = renderable(values.get("file"))

        logging.debug("Saving %s to %s...", values.get("file"), values.get("output") or "terminal")
        output = self.get_output(**values)
        output.write(rendered)
        output.close()

def main():
    try:
        Loader()()
    except Exception as e:
        logging.error("(%s): %s", e.__class__.__name__, e)
        exit(1)

if __name__ == "__main__":
    main()
