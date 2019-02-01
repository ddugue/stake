import logging

from . import base
from stake import params
from jinja2.ext import i18n
from jinja2 import Environment

@params.string("i18n:language", help="Language for to render with", short="l")
@params.string("i18n:main", help="Main language for to render with", default=None)
@params.string("i18n:locale_dir", help="Directory for locales", default="assets/locales")
class i18nExtension(base.Extension):
    def get_context_data(self) -> dict:
        "Replace current context data url function with an i18n one"
        ctxt = super(i18nExtension, self).get_context_data()
        ctxt["lang"] = getattr(self, "language")
        if "url" in ctxt:
            def url(uri, override=None):
                lang = override or getattr(self, "language")
                if lang == getattr(self, "main"):
                    return uri
                return "/%s%s" % (lang, uri)
            ctxt["url"] = url
        return ctxt

    def get_translations(self):
        "Return translations for the jinja2"
        try:
            from babel.support import Translations
        except ImportError:
            logging.error("""
            Could not import babel, make sure babel is installed.

            You can install babel with `pip install babel`
            """)
            raise
        locale_dir = getattr(self, "locale_dir")
        lang = getattr(self, "language")
        return Translations.load(locale_dir, [lang])

    def get_environment(self) -> Environment:
        env = super().get_environment()
        env.add_extension(i18n)
        env.install_gettext_translations(self.get_translations())
        return env

__default__ = i18nExtension
