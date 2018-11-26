
import os
from glob import glob

from . import base
from .. import logging
from stake import params

class File:
    def __init__(self, path):
        self.path = path
        self.content = None

    def open(self):
        """ Open and read file """
        with open(self.path, 'r') as file:
            return ''.join(file.readlines())

    def _parse_yml(self):
        try:
            import yaml
            return yaml.safe_load(self.open())
        except ImportError as e:
            logging.error("""
            Could not find yaml parser,

            make sure that PyYAML is install with:
            `pip install PyYAML` to enable yaml parsing
            """)
            raise e

    def parse(self):
        if not self.content:
            if self.path.endswith('yml'):
                self.content = self._parse_yml()
            else:
                self.content = self.open()
        return self.content

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def __getattr__(self, attr):
        #only called what self.attr doesn't exist
        return self.parse()[attr]

    def __getitem__(self, attr):
        return self.parse()[attr]

    pass

@params.boolean("files:ignore_empty", help="Do not raise an error on empty set",
                default=False, is_cli=False)
@params.string("files:files_directory",
               help="Working directory to resolve file paths (use same working directory as templates by default)",
               default='', is_cli=False)
class FileExtension(base.Extension):
    def get_context_data(self) -> dict:
        "Add functions to fetch files information from a directory"
        ctxt = super().get_context_data()
        directory = getattr(self, "files_directory") or  getattr(self, "cwd")
        ignore_empty = getattr(self, "ignore_empty")

        def get_files(pattern):
            "Return files obtained through glob"
            full_pattern = os.path.join(directory, pattern)
            files = [File(f) for f in glob(full_pattern)]
            if not len(files) and not ignore_empty:
                logging.error("""
                Could not find any files with the pattern %s.

                We looked for files according to relative folder %s. If you
                want to change this relative folder, you can set the 'directory'
                parameter

                If you want to deactivate this type of error, you can set
                ignore_empty parameter.
                """ % (pattern, directory))
                raise ValueError("Couldn't find any files")
            return files

        ctxt["files"] = get_files
        return ctxt

__default__ = FileExtension
