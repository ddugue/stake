
from jinja2 import Environment
from renderer import Renderer

class Extension(Renderer):
    "Base class to extend, decorator pattern to allow extension"

    def __init__(self, renderer, **kwargs):
        self.renderer = renderer
        super().__init__(**kwargs)

    def get_environment(self) -> Environment:
        """Create or extends the Jinja2 Environment,

        use add_extension or Overlay to extend it
        """

        return self.renderer.get_environment()

    def get_context_data(self) -> dict:
        "Create or extends the context for the rendering of a template"

        return self.renderer.get_context_data()

    def get_render_fn(self):
        """Return a function to render

        The function takes a jinja2 environment,
        a ctxt_data and a file to render
        """

        return self.renderer.get_render_fn()
