from . import base
import params

@namespace("i18n")
@params.string("language", short="l")
class i18nExtension(base.extension):
    def get_context_data(self) -> dict:
        ctxt = super(i18nExtension, self).get_context_data()
        ctxt.update({
            ""
        })
        if "url" in ctxt:
            ctxt["url"] = lambda uri: uri
        return ctxt

    class Meta:
        jinja2_extensions = ("")
        cli_arguments = (
            {"arg":"language"}
        )
