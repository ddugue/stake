import unittest
import uuid
import os
import sys
from config.ini import IniConfigParser
FILE_CONTENT = """
[SECTION]
subkey = value

[TEST]
key = value
"""

class FileParsingTest(unittest.TestCase):
    parser = IniConfigParser()

    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = open("/tmp/"+self.uuid, "w+")
        self.file.write(FILE_CONTENT)
        self.file.seek(0)

    def test_file_treatment(self):
        config = self.parser(config_file=self.file)
        self.assertIsNotNone(config)

    def test_section_parsing(self):
        config = self.parser(config_file=self.file)
        self.assertIsNotNone(config)
        self.assertEqual(config["SECTION"], {"subkey":"value"})

    def test_variable(self):
        config = self.parser(config_file=self.file)
        self.assertEqual(config["TEST"]["key"], "value")

    def test_additional_arguments(self):
        config = self.parser(config_file=self.file, a=2)
        self.assertEqual(config["a"], 2)

    def test_override_arguments(self):
        config = self.parser(config_file=self.file, **{"TEST":{"key":"overrideValue"}})
        self.assertEqual(config["TEST"]["key"], "overrideValue")

    def tearDown(self):
        self.file.close()
        os.remove("/tmp/"+self.uuid)


