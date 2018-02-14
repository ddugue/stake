import os

from stake import params
from . import base
from .. import logging

@params.file("data:file", short="D", help="File path of the file")
class DataExtension(base.Extension):
    """ Provides extension to load a data set from a file

    Can load data file from .json, .yaml and .xml based on file extension
    """

    def load_data(self) -> dict:
        f = getattr(self, "file")
        ext = os.path.splitext(f.name)[1]
        if ext == '.json':
            logging.debug("Opening file %s as JSON", f.name)
            import json
            return json.load(f)

        elif ext == '.yml' or ext == '.yaml':
            logging.debug("Opening file %s as YAML", f.name)
            try:
                import yaml
                return yaml.safe_load(f)
            except ImportError as e:
                logging.error("""
                Could not find yaml parser,

                make sure that PyYAML is install with:
                `pip install PyYAML` to enable yaml parsing
                """)
                raise e

        elif ext == '.xml':
            logging.debug("Opening file %s as XML", f.name)

    def get_context_data(self) -> dict:
        "Extends the context data with an url function"
        ctxt_data = super().get_context_data()
        ctxt_data["data"] = self.load_data()
        return ctxt_data


__default__ = DataExtension
