import uuid
import unittest
import os

from renderer import Renderer
from extensions.base import Extension
FILE_CONTENT = """{{1+1}}"""

class DummyExtensionTest(unittest.TestCase):
    extension_cls = Extension
    args = {}

    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = open("/tmp/"+self.uuid, "w+")
        self.file.write(FILE_CONTENT)
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
