from argparse import ArgumentParser

# Need data for configuring each 'extension'
# For example a Data extension, might need a data folder argument

class BaseZen():
    """Base Zen class that lists the member of every Zen object"""

    # List of jinja2 extensions
    jinja2_ext = []

    def configure_object(self, **kwargs) -> dict:
        """Configure Zen and adds configuration if desired"""
        return kwargs

    def configure_parser(self, parser:ArgumentParser) -> ArgumentParser:
        """Configure Zen and adds configuration if desired"""
        return parser

    def get_jinja2_ext(self) -> string[]:
        """Return a string list of jinja2 extensions"""
        return self.jinja2_ext

    def prerender(self, file:File) -> File:
        """Hook to modify the file before its rendering"""
        return file

    def get_context_data(self, **kwargs) -> dict:
        """Create or extends the context for the rendering"""
        return kwargs

    def render(self, output:string="") -> string:
        """Modify or create the output"""
        return output



class BaseZenExtension(BaseZen):
    """Base class for Zen extensions"""

    # List of Hard dependencies
    hard_dependencies = []

    # List of Soft dependencies
    soft_dependencies = []

    def get_hard_dependencies(self) -> string{}:
        """Return a set of necessary dependencies

        Return the list of all the necessary depencies which will
        be loaded only absolute requirements for the extension
        to work

        """
        return self.hard_dependencies

    def get_soft_dependencies(self) -> string{}:
        """Return a list of soft dependencies

        Returns a list of extensions which are not necessary for the
        extension to work, but should nevertheless be loaded BEFORE
        this dependency

        """
        return self.soft_dependencies


class BaseZenRenderer(BaseZen):
    """Main renderer class used by Zen"""

    # String list of Zen extensions to load and include
    extensions = []

    #-- Initialization methods
    def get_extensions(self) -> BaseZenExtension{}:
        """Returns an ordered set of all the loaded zen extensions"""
        # TODO: Implement initialization
        if not self._extensions:
            self._extensions = []
        return self._extensions

    def configure_parser(parser):
        """Configure parser's arguments"""

        parser.add_argument("src", help="Filename to render")
        parser.add_argument("--root",
                                 help="Path to the template root folder")
        for ext in self.get_extensions():
            ext.configure_parser(parser)
        return parser


    def configure_object(self) -> dict:
        """Configure config object

        Configure configuration object (dict) based on the argparse
        arguments and base on every extensions configuration
        """

        # TODO: Refactor using reduce
        self.config = vars(self.parser.parse_args())
        for ext in self.get_extensions():
            self.config = ext.configure_object(self.config)
        return self.config

    def __init__(self):
        # First we configure parser
        self.parser = self.configure_parser(
            ArgumentParser(description=PRODUCT_DESCRIPTION))

        # Then we configure the object based on the parser
        self.configure_object()

    def get_jinja2_ext(self) -> string{}:
        # TODO: Refactor using reduce
        jinja2_extensions = set()
        for ext in self.get_extensions():
            jinja2_extensions = jinja2_extensions & ext.get_jinja2_ext()
        return jinja2_extensions

    def get_loader(self) -> Loader:
        """Returns a Jinja2 Loader object for rendering"""
        pass

    def get_environment(self) -> Environment:
        """Returns a Jinja2 Environment object"""
        return Environment(loader=self.get_loader(),
                           extensions=list(self.get_jinja2_ext()))

    def get_context_data(self, **context) -> dict:
        """Returns all the aggregated context of the extensions"""
        # TODO: Refactor using reduce
        for ext in self.get_extensions():
            context = ext(**context)
        return context

    def render(self) -> string:
        """Renders a jinja2 template"""
        template = self.get_environment().get_template(self.config.src)
        return template.render(**self.get_context_data())

    def __call__(self):
        return self.render()

