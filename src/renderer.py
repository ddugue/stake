
from jinja2 import Environment, BaseLoader, FileSystemLoader
import params

@params.string("cwd", default=".")
@params.namespace("site")
class Renderer:
    """Renders a file in an extensible way"""

    def __init__(self, **kwargs):
        for k, item in kwargs.items():
            setattr(self, k, item)

    def get_loader(self) -> BaseLoader:
        """Returns a Jinja2 Loader object for rendering"""
        return FileSystemLoader(getattr(self, "cwd"))

    def get_environment(self):
        """Returns the jinja2 environment"""
        return Environment(loader=self.get_loader())

    def get_context_data(self) -> dict:
        """Returns a dict of the ctxt data"""
        return {
            "site": getattr(self, "site")
        }

    def get_render_fn(self):
        """Return a callable that takes environment, ctxt_data and file"""
        def render(environment, ctxt_data, file_path):
            "Renders a jinja2 template"
            template = environment.get_template(file_path)
            return template.render(**ctxt_data)
        return render

    def __call__(self, file_path) -> str:
        """Render a file.

        Calls get_render_fn and inputs get_environment(),
        get_context_data() and returns the render
        """
        render = self.get_render_fn()
        environment = self.get_environment()
        context_data = self.get_context_data()
        return render(environment, context_data, file_path)
