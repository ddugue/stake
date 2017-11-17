
import configparser

from stake import params
from . import base

@params.integer("fm:allowed_skip", default=3)
@params.string("fm:identifier", short="I", default="--")
class FrontMatterExtension(base.Extension):
    """Provides an extension that adds front matter parsing

    Only difference with Jekyll, is we use a more versatile ini format.
    We also allow encourage to put data in a commented format to
    respect syntax highlighter
    """

    def extract_lines(self, filename, jinja2_env):
        "Extract lines of config at the beginning of the file"

        has_started = False
        lines = []

        # Identifiying string to delimit a front matter block
        identifier = getattr(self, "identifier")
        # Number of lines we Could skip before reaching identifier
        allowed_skip = getattr(self, "allowed_skip")
        template = jinja2_env.get_template(filename)

        with open(template.filename, "r", encoding="utf-8") as opened_file:
            for line in opened_file:
                if len(lines) > allowed_skip and not has_started:
                    # It means there was no identifier in the first lines
                    return []


                if has_started and (identifier in line):
                    # When we reach the second identifier
                    lines.append("")
                    break
                # We append skipped lines, so we can keep track of lines in
                # file
                lines.append(line.strip("#/ \n") if has_started else "")

                has_started = has_started or identifier in line

        return lines

    @staticmethod
    def parse_lines(config_string, jinja2_env, **ctxt):
        "Renders and loads the config and returns its values"
        config_string = "[Page]\n%s" % config_string
        rendered = jinja2_env.from_string(config_string).render(**ctxt)
        config = configparser.ConfigParser()
        try:
            config.read_string(rendered)
        except configparser.ParsingError:
            return {}
        return dict(config.items("Page"))

    def get_render_fn(self):
        render_fn = super().get_render_fn()
        def render(environment, ctxt_data, file_path):
            "Before rendering the template, loads the front matter"
            lines = self.extract_lines(file_path, environment)
            page = self.parse_lines("\n".join(lines), environment, **ctxt_data)
            ctxt_data["page"] = page

            output = render_fn(environment, ctxt_data, file_path)

            # Before returing output, we strip the front matter block
            return "\n".join(output.split("\n")[len(lines):])
        return render

__default__ = FrontMatterExtension
