import logging

import os
import logging
from . import base
from stake import params
from jinja2 import Environment
from jinja2.ext import i18n
from jinja2 import Environment

# TODO: Add other i18n parameters to allow better customization
@params.string("i18n:language", help="Language for to render with", short="l")
@params.string("i18n:main", help="Main language for to render with", default=None)
@params.string("i18n:locale_dir", help="Directory for locales", default="assets/locales")
@params.boolean("i18n:ignore_errors", help="Ignore errors", is_cli=False, default=False)
class I18nExtension(base.Extension):


    def get_context_data(self) -> dict:
        "Replace current context data url function with an i18n one"
        ctxt = super().get_context_data()
        ctxt["lang"] = getattr(self, "language")
        ctxt["LANG"] = getattr(self, "language")
        ctxt["language"] = getattr(self, "language")
        ctxt["current_lang"] = getattr(self, "language")
        ctxt["CURRENT_LANG"] = getattr(self, "language")
        ctxt["current_language"] = getattr(self, "language")

        # We decorate url function with additional lang keyword
        if "url" in ctxt:
            uri_fn = ctxt["url"]
            def get_url(*args, **kwargs):
                kwargs['lang'] = kwargs.get("lang", ctxt["lang"])
                return uri_fn(*args, **kwargs)
            ctxt["url"] = get_url

        return ctxt

    def get_translations(self):
        "Return translations for the jinja2"
        try:
            from babel.support import Translations
        except ImportError:
            logging.error("""
            Could not import babel, make sure babel is installed.

            You can install babel with `pip install Babel`
            """)
            raise
        locale_dir = getattr(self, "locale_dir")
        lang = getattr(self, "language")
        return Translations.load(locale_dir, [lang])

    def get_environment(self) -> Environment:
        "Return a decorated environment with Jinja2 extension installed"
        env = super().get_environment()
        translations = self.get_translations()
        if not translations._catalog and not getattr(self, "ignore_errors"):
            path = os.path.join(
                os.getcwd(),
                getattr(self, "locale_dir"),
                getattr(self, "language"),
                "LC_MESSAGES",
                "messages.po",
            )
            logging.error("""
            The MO Catalog could not be found or is empty.

            Make sure that the compiled po file (.mo) is not empty:
            %s
            """ % path)
            raise ValueError('No translations found!')
        logging.debug(translations)
        env.add_extension(i18n)
        env.install_gettext_translations(self.get_translations())
        return env

__default__ = i18nExtension
