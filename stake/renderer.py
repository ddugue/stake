import os
import logging

from . import logging

from jinja2 import Environment, BaseLoader, FileSystemLoader, TemplateNotFound, \
    UndefinedError, Undefined

class SilentUndefined(Undefined):
    """ Dont break pageloads because vars arent there! """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.error('Variable %s was undefined!' % self.name)
        return None

from . import params

@params.string("cwd", default=".")
@params.boolean("silence_undefined", default=False,
                help="Option to silence undefined variable in template rendering")
@params.namespace("site")
class Renderer:
    """Renders a file in an extensible way"""

    def __init__(self, **kwargs):
        for k, item in kwargs.items():
            setattr(self, k, item)

    def get_loader(self) -> BaseLoader:
        """Returns a Jinja2 Loader object for rendering"""
        return FileSystemLoader(getattr(self, "cwd"))

    def get_environment(self) -> Environment:
        """Returns the jinja2 environment"""
        if self.silence_undefined:
            return Environment(loader=self.get_loader(), undefined=SilentUndefined)
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
            logging.debug("Rendering with context data %s", ctxt_data)

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

        try:
            return render(environment, context_data, file_path)

        except TemplateNotFound as e:
            path = os.path.abspath(os.path.join(getattr(self, "cwd"))
            logging.error("""
            Could not found template %s. Make sure that template %s exists and
            is readable.

            You can change directory for templates, by setting the 'cwd' argument
            via your config or via the command line.
            """, e, path, str(e)))
            raise

        except UndefinedError as e:
            logging.error("""
            Template variable %s. Make sure that your context data has that value. You can print
            your context data by enabling the '--verbose' argument.

            Additionally, you can silence undefined variable in Jinja2 by turning
            the '--silence_undefined' argument
            """, e)
            raise

        except Exception as e:
            logging.error(e)
            logging.error(e.__class__)
            raise
