from . import base
from stake import params

@namespace("i18n")
@params.string("language", short="l")
class I18nExtension(base.extension):
    def get_context_data(self) -> dict:
        ctxt = super(i18nExtension, self).get_context_data()
        ctxt.update({
            ""
        })
        if "url" in ctxt:
            ctxt["url"] = lambda uri: uri
        return ctxt

__default__ = I18nExtension
