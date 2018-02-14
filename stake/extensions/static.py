from stake import params
from . import base

@params.string("static:prefix", help="Prefix for a static file", default="")
class StaticFileExtension(base.Extension):
    """ Provides extension to abstract static file path generation

    Similar to Django's own staticfile app
    """

    def get_static_fn(self):
        """ Return the lambda to use for path generation """
        prefix = getattr(self, "prefix")
        return lambda path: prefix + path

    def get_context_data(self) -> dict:
        "Extends the context data with an url function"
        ctxt_data = super().get_context_data()
        ctxt_data["static"] = self.get_static_fn()
        return ctxt_data


__default__ = StaticFileExtension
