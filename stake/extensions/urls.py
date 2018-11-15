"""Extension that allows the user to reference url"""
import os
import sys
import importlib
import logging

from stake import params
from . import base

# URL_FORMAT = ("name", {"args":"values"}, "url")
URL_NAME = 0
URL_ARGS = 1
URL_URL = 2

@params.string("url:urls", default="etc/urls", help=("Python file containing "
                                                       "the list of url"))
@params.string("url:base_url", default="/", help=("Base url to prefix all urls"))
class UrlExtension(base.Extension):
    """Provides an extension that loads a url

    Support for multi languages is provided by the i18n extension
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__urls = None

    @staticmethod
    def import_url_module(url_path):
        "Convulted way to import a python file as a config"
        is_absolute = url_path.startswith("/")
        folders = url_path.split("/")
        path = "/".join(folders[:-1]) + "/"
        # We append the PATH
        module = folders[-1]
        module_name = module.split(".")[0]
        if is_absolute:
            sys.path.append(path)
            spec = importlib.util.spec_from_file_location(module_name, url_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            cwd = os.getcwd()
            sys.path.append(os.path.join(cwd, path))
            return importlib.import_module(module_name)


    def get_urls(self):
        "Load and returns the urls located in iterator / list URLS in the config"
        if not self.__urls:
            python_url_path = getattr(self, "urls")
            try:
                url_module = self.import_url_module(python_url_path)
            except ModuleNotFoundError as e:
                logging.error(""" Could note import url module!

                Make sure that parameter urls is set to a python file that
                can be imported! Tried importing config file %s.py
                """ % python_url_path)
                raise
            self.__urls = list(getattr(url_module, "URLS", []))
        return self.__urls


    def get_url(self, name, **args):
        "Returns a specific url or a default one if the specific is not found"
        base_url = getattr(self, "base_url")

        def is_in(tup):
            return tup[0] in args and tup[1] == args[tup[0]]

        for url in self.get_urls():
            if url[URL_NAME] == name:
                is_match = all(map(is_in, url[URL_ARGS].items()))
                if is_match:
                    return base_url + url[URL_URL]

        if "default" not in args:
            # If there is no match we try to find a fallback url
            return self.get_url(name, default=True)

        return None


    def get_context_data(self) -> dict:
        "Extends the context data with an url function"

        ctxt_data = super().get_context_data()
        ctxt_data["url"] = self.get_url
        return ctxt_data


__default__ = UrlExtension
