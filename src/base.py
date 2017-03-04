from jinja2 import Environment

class Renderer(object):
    """Renders a file in an extensible way"""
    def get_loader(self) -> Loader:
        """Returns a Jinja2 Loader object for rendering"""
        pass

    def get_environment(self):
        """Returns the jinja2 environment"""
        return Environment(loader=self.get_loader())

    def get_context_data(self) -> dict:
        """Returns a dict of the ctxt data"""
        return {}

    def get_render_fn(self):
        """Return a callable that takes environment, ctxt_data and file"""
        def render(environment, ctxt_data, file):
            template = environment.get_template(file)
            return template.render(**ctxt_data)

    def __call__(self, file) -> str:
        """Render a file.

        Calls get_render_fn and inputs get_environment(),
        get_context_data() and returns the render"""
        render = self.get_render_fn()
        environment = self.get_environment()
        context_data = self.get_context_data()
        return render(environment, context_data, file)
