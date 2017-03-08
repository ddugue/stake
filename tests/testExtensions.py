import uuid
import unittest
import os
import sys

from renderer import Renderer
from extensions.base import Extension
from extensions.frontmatter import FrontMatterExtension
from extensions.urls import UrlExtension

class TestUtilsMixin:
    def create_file(self, file_name, content):
        "Create a temporary file with content"

        file_instance = open("/tmp/" + file_name, "w+")
        file_instance.write(content)
        file_instance.seek(0)
        return file_instance

FILE_CONTENT = """{{1+1}}"""

class DummyExtensionTest(unittest.TestCase, TestUtilsMixin):
    extension_cls = Extension
    template = FILE_CONTENT
    args = {}

    def get_args(self):
        "Return the extension_class arguments"
        return self.args

    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = self.create_file(self.uuid, self.template)

        kwargs = self.get_args()
        self.renderer = self.extension_cls(Renderer(cwd="/tmp/"), **kwargs)

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

URL_FILE_CONTENT = """
{{url("contact")}}
{{url("home")}}
{{url("post", date="2012-05-06")}}
{{url("post", data="2013-06-08")}}
"""

URL_PYTHON_FILE_CONTENT = """
URLS = [
    ("contact", {}, "contact"),
    ("home", {}, ""),
    ("post", {"date":"2012-05-06"}, "blog/2012-05-06"),
    ("post", {"default":True}, "blog/"),
]
"""

class UrlExtensionTest(unittest.TestCase, TestUtilsMixin):
    """Tests the url extension"""
    extension_cls = UrlExtension
    template = URL_FILE_CONTENT
    python_template = URL_PYTHON_FILE_CONTENT

    def get_args(self):
        return {"url:config": "/tmp/" + self.python_uuid}

    def setUp(self):
        self.previous_path = sys.path.copy()

        self.python_uuid = str(uuid.uuid4()).replace("-","") + ".py"
        self.python_file = self.create_file(self.python_uuid, self.python_template)

        self.uuid = str(uuid.uuid4())
        self.file = self.create_file(self.uuid, self.template)

        kwargs = self.get_args()
        print(kwargs)
        self.renderer = self.extension_cls(Renderer(cwd="/tmp/"), **kwargs)


    def test_url_root(self):
        "Ensure that a root url works"
        self.assertEqual(self.renderer.get_url("home"), "/")

    def test_url_normal(self):
        "Ensure that a normal url works"
        self.assertEqual(self.renderer.get_url("contact"), "/contact")

    def test_prefix(self):
        "Ensure that the prefix parameter for config works"
        kwargs = self.get_args()
        kwargs["url:base_url"] = "http://google.com/"
        self.renderer = self.extension_cls(Renderer(cwd="/tmp/"), **kwargs)
        self.assertEqual(self.renderer.get_url("contact"),
                         "http://google.com/contact")


    def test_url_args(self):
        "Ensure that a url with args get sent properly"
        self.assertEqual(self.renderer.get_url("post", date="2012-05-06"),
                         "/blog/2012-05-06")

    def test_url_default(self):
        "Ensure that the default url is sent correctly"
        self.assertEqual(self.renderer.get_url("post", date="2013-05-06"),
                         "/blog/")

    def test_nonexisting_url(self):
        "Ensure that a non-existing url returns None"
        self.assertEqual(self.renderer.get_url("blab", date="2013-05-06"),
                         None)

    def test_render(self):
        "Ensures that the extension can render a simple jinj2 file"
        self.assertEqual(self.renderer(self.uuid),
                         "\n/contact\n/\n/blog/2012-05-06\n/blog/")

    def test_relative_import(self):
        "Ensure that we can import relatively"
        kwargs = self.get_args()
        kwargs["url:config"] = "tests/urlconf.py"
        self.renderer = self.extension_cls(Renderer(cwd="/tmp/"), **kwargs)
        urls = self.renderer.get_urls()
        self.assertEqual(urls, [("test", {}, "test")])

    def tearDown(self):
        self.file.close()
        self.python_file.close()
        os.remove("/tmp/"+self.uuid)
        os.remove("/tmp/"+self.python_uuid)
        sys.path = self.previous_path
