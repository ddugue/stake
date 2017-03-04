from base import Renderer
FILE_CONTENT = """
{{1+1}}
"""
class RendererTest(unittest.TestCase):
    def setUp(self):
        self.uuid =str(uuid.uuid4())
        self.file = open("/tmp/"+self.uuid, "w+")
        self.file.write(FILE_CONTENT)
        self.file.seek(0)
        self.renderer = Renderer()

    def test_context_data(self):
        self.assertIsNotNone(self.renderer.get_context_data())

    def test_environment(self):
        self.assertIsNotNone(self.renderer.get_context_data())

    def test_render(self):
        self.assertEqual(self.renderer(self.file), "2")

    def tearDown(self):
        self.file.close()
        os.remove("/tmp/"+self.uuid)

