import uuid
import unittest
import os

from renderer import Renderer

FILE_CONTENT = """{{1+1}}"""
class RendererTest(unittest.TestCase):
    "Tests to ensure our Renderer work"
    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = open("/tmp/"+self.uuid, "w+")
        self.file.write(FILE_CONTENT)
        self.file.seek(0)
        self.renderer = Renderer(cwd="/tmp/")

    def test_context_data(self):
        "Test that the renderer can return context data"
        self.assertIsNotNone(self.renderer.get_context_data())

    def test_loader(self):
        "Test that the renderer can return a loader"
        self.assertIsNotNone(self.renderer.get_loader())

    def test_environment(self):
        "Test that the renderer can return an environment"
        self.assertIsNotNone(self.renderer.get_environment())

    def test_render_fn(self):
        "Test that the renderer can return a rendering function"
        self.assertIsNotNone(self.renderer.get_render_fn())

    def test_render(self):
        "Test that the renderer can render a simple jinja 2 file"
        self.assertEqual(self.renderer(self.uuid), "2")

    def tearDown(self):
        self.file.close()
        os.remove("/tmp/"+self.uuid)

class SiteVariableLoadingTest(unittest.TestCase):
    "Tests linked to site variable loading"
    def test_site_variables(self):
        "Test that the site variables are in the context_data"
        config_data = {
            "site:facebook": "FacebookURL",
            "site:twitter": "TwitterURL"
        }
        renderer = Renderer(**config_data)
        ctxt = renderer.get_context_data()
        self.assertEqual(ctxt, {
            "site": {
                "facebook": "FacebookURL",
                "twitter": "TwitterURL"
            }
        })
