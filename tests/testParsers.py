import unittest
import uuid
import os
import params
from config.ini import parser as configparser

file_content = """[Base]
first_level = 1

[SECTION]
subkey = value

[TEST]
key = value
"""
class FileParsingTest(unittest.TestCase):
    "Generic test to test a parser"


    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.path = "/tmp/"+self.uuid
        self.file = open(self.path, "w+")
        self.file.write(file_content)
        self.file.seek(0)

    def get_parser(self):
        return configparser

    def test_no_file(self):
        "When no config file is provided, it should raise an error"
        with self.assertRaises(params.MissingParameterError):
            self.get_parser()()

    def test_file_treatment(self):
        "Ensures that parser returns a value"
        config = self.get_parser()(config_file=self.path)
        self.assertIsNotNone(config)

    def test_base(self):
        "Ensures that parser handles first level values"
        config = self.get_parser()(config_file=self.path)
        print(config)
        self.assertEqual(config["first_level"], "1")

    def test_section_parsing(self):
        "Ensures that parser handles section and subkey correctly"
        config = self.get_parser()(config_file=self.path)
        self.assertIsNotNone(config)
        print(config)
        self.assertEqual(config["section:subkey"], "value")

    def tearDown(self):
        self.file.close()
        os.remove("/tmp/"+self.uuid)
