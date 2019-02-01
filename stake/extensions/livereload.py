""" Extension to inject a livereload script """
from stake import params

from . import base
from .. import logging

@params.integer("livereload:port", help="Port used for the livereload scritpt",
                default="35729", is_cli=False)
@params.string("livereload:tag", help="Tag where we inject the livereload before",
               default="</body>", is_cli=False)
@params.boolean("development", short="d", help="Enable devtools")
class LiveReloadExtension(base.Extension):
    "Extension that injects a livereload script into the page"

    def get_render_fn(self):
        "We override render function to pre-parse the file to fetch more context"
        render_fn = super().get_render_fn()
        def render(environment, ctxt_data, file_path):
            "After rendering the template we inject the livereload script"
            output = render_fn(environment, ctxt_data, file_path)

            development = getattr(self, "development")
            if not development: return output

            port = getattr(self, "port")
            tag = getattr(self, "tag")

            script = """<script>
            document.write('<script src="http://'
            + (location.host || 'localhost').split(':')[0]
            + ':%s/livereload.js?snipver=1"></'
            + 'script>')
            </script>""" % port + "%s" % tag
            new_output = output.replace('%s' % tag, script)
            if output == new_output:
                logging.warning("Could not inject the livereload script.")
                logging.warning(
                    """The livereload extension uses the html {0} tag to inject
the script. Make sure that your html template contains an {0} tag.
                    """.format(tag)
                )
            return new_output

        return render

__default__ = LiveReloadExtension
