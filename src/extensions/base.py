class Extension(Renderer):
    def __init__(self, renderer, **kwargs):
        self.renderer = renderer

    def get_environment(self) -> Environment:
        """Create or extends the Jinja2 Environment, use add_extension
        or Overlay to extend it"""
        return self.renderer.get_environment()

    def get_context_data(self) -> dict:
        """Create or extends the context for the rendering of a template
        """
        return self.renderer.get_context_data()

    def get_render(self):
        """Return a function that takes a jinja2 environment, a ctxt_data and a file to render"""
        return self.renderer.get_render_fn()

    class Meta:
        namespace = ""
        jinja2_extensions = ()
        cli_arguments = ()


"""
class Tex(Extension):
    def get_render_fn(self):
        super_fn = super(TEx, self).get_render_fn()
        def overwrite(environment, ctxt_data, file):
            ctxt_data["this"] = "bla"
            render = super_fn(environment, ctxt_data, file)
            render += "DAMN"
        return overwrite
"""
