# Need data for configuring each 'extension'
# For example a Data extension, might need a data folder argument

class BaseZen():
    """Base Zen class that lists the member of every Zen object"""

    # List of jinja2 extensions
    jinja2_ext = []

    def __init__(self, parser:ArgumentParser):
        """Initialize the parser's arguments"""
        pass

    def configure(self, **kwargs) -> dict:
        """Configure Zen and adds configuration if desired"""
        return kwargs

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


class ZenRenderer(BaseZen):
    """Main renderer class used by Zen"""

    # string list of Zen extensions
    extensions = []

    def get_extensions(self) -> BaseZenExtension{}:
        return []

    def get_loader(self) -> Loader:
        pass

    def get_environment(self) -> Environment:
        pass

    def __init__(self):
        pass

    def __call__(self):
        """Renders"""
        pass

