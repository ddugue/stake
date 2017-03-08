import uuid
import unittest
import os

from renderer import Renderer
from extensions.base import Extension
from extensions.frontmatter import FrontMatterExtension

FILE_CONTENT = """{{1+1}}"""

class DummyExtensionTest(unittest.TestCase):
    extension_cls = Extension
    template = FILE_CONTENT
    args = {}

    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = open("/tmp/"+self.uuid, "w+")
        self.file.write(self.template)
        self.file.seek(0)
        self.renderer = self.extension_cls(Renderer(cwd="/tmp/"), **self.args)

    def test_context_data(self):
        "Ensures that the extension returns context data"
        self.assertIsNotNone(self.renderer.get_context_data())

    def test_loader(self):
        "Ensures that the extension returns a loader"
        self.assertIsNotNone(self.renderer.get_loader())

    def test_environment(self):
        "Ensures that the extension returns an environment"
        self.assertIsNotNone(self.renderer.get_environment())

    def test_render_fn(self):
        "Ensures that the extension returns a rendering function"
        self.assertIsNotNone(self.renderer.get_render_fn())

    def test_render(self):
        "Ensures that the extension can render a simple jinj2 file"
        self.assertEqual(self.renderer(self.uuid), "2")

    def tearDown(self):
        self.file.close()
        os.remove("/tmp/"+self.uuid)

FRONTMATTER_FILE_CONTENT = """
<!--
name_test = Boom
test_int = {{1+1}}
-->
{{page.name_test}}
"""
class FrontmatterExtensionTest(DummyExtensionTest):
    extension_cls = FrontMatterExtension
    template = FRONTMATTER_FILE_CONTENT

    def test_extract_lines(self):
        "Ensures that we can extract the lines from the file"
        lines = self.renderer.extract_lines(
            self.uuid,
            self.renderer.get_environment()
        )
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines,
                         ["","","name_test = Boom", "test_int = {{1+1}}", ""])

    def test_parsing(self):
        "Ensures that we can parse to a config file easily"
        config = "name_test = Boom\ntest_int = {{1+1}}"
        values = self.renderer.parse_lines(
            config,
            self.renderer.get_environment()
        )
        self.assertEqual(values["test_int"], "2")

    def test_invalid_parsing(self):
        "Ensures that invalid parsing doesn't make the program crash"
        config = "%SAD@$$"
        values = self.renderer.parse_lines(
            config,
            self.renderer.get_environment()
        )
        self.assertEqual(values, {})

    def test_parsing_with_ctxt(self):
        "Ensures that invalid parsing doesn't make the program crash"
        config = "name_test = Boom\ntest_int = {{baba}}"
        values = self.renderer.parse_lines(
            config,
            self.renderer.get_environment(),
            **{"baba": 2}
        )
        self.assertEqual(values["test_int"], "2")

    def test_render(self):
        "Ensures that the extension can render a simple jinj2 file"
        self.assertEqual(self.renderer(self.uuid), "Boom")
