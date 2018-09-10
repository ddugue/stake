#-- Imports
import types
import logging

LOGGER = logging.getLogger("stake")

__all__ = ["string", "boolean", "integer", "choice", "array"]
#-- Constants
ARGPARSE_PARAMETERS = set()

#-- Exceptions
class ParsingError(Exception):
    """Triggered when there is an error parsing a parameter"""

    def __init__(self, parameter, cls_name, *args, **kwargs):
        self.parameter = parameter
        self.cls_name = cls_name
        super().__init__(*args, **kwargs)

class MissingParameterError(ParsingError):
    """Triggered when there's a missing parameter upon parsing"""

    def __str__(self):
        msg = ("%s is missing for %s, make sure to either add a default value"
               " for the parameter or provide its value")
        return msg % (self.parameter.name, self.cls_name)

class InvalidCastError(ParsingError):
    """Triggered when there's an invalid type casting upon parsing"""

    def __init__(self, value_error, *args, **kwargs):
        self.value_error = value_error
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s could not be cast with %s on %s: %s" % (
            self.parameter.name,
            repr(self.parameter.cast),
            self.cls_name,
            str(self.value_error)
        )


def get_value(key):
    "Returns value name of a key in format namespace:key"
    return key.split(":")[-1]

def get_namespace(key):
    "Returns the namespace of a key in a format namespace:key"
    if not ":" in key:
        return None
    return ".".join(key.split(":")[:-1])

#-- Classes
class Parameter():
    """Handles the representation of a configuration parameter"""
    cast = lambda x: x

    def __init__(self, name, is_cli=True, **argparse_kwargs):
        """Configure a parameter:

        name = Name of the parameter in the format namespace:argument
        is_cli = Wether ArgparseArgument should add this parameter
                 to an argparse
        argparse_kwargs = Arguments to send to ArgparseArgument
        * default = If provided, will be in argparse_kwargs
        * help = If provided, will be in argparse_kwargs
        """
        # Name of the parameter
        self.name = name
        self.is_cli = is_cli

        # Args to pass to argparse
        self.argparse_kwargs = argparse_kwargs

        # We register the instance of the parameter to our singleton
        ARGPARSE_PARAMETERS.add(self)

    def __call__(self, wrapped):
        "Validate argument before sending it to fn or class"
        is_fn = isinstance(wrapped, types.FunctionType)
        wrapped_fn = wrapped if is_fn else wrapped.__init__

        def validate_args(*args, **kwargs):
            "Wrapping function that validates the args sent"
            # We get the namespace of the current argument
            try:
                return wrapped_fn(*args, **self.parse(kwargs, name=wrapped.__name__))
            except TypeError as e:
                args = str(e).split(":")[-1]
                LOGGER.error("""
                Could not validate the arguments {} for {}.

                Make sure to include all arguments either from cli or configuration
                file and that no extensions are shadowing the context

                Original error: {}""".format(args, wrapped_fn.__name__ if is_fn else wrapped.__name__, str(e)))
                raise

        if not is_fn:
            wrapped.__init__ = validate_args
            return wrapped # If is a class we return a class
        return validate_args # If is a function we return a function

    def convert(self, value):
        """Cast the value to the desired type, raise value error on impossible cast"""
        return self.__class__.cast(value)

    def parse(self, kwargs, name=None):
        """Change parameter object value for this parameter on kwargs"""
        kwargs = kwargs.copy()

        if self.name in kwargs:
            # We try first to get the value directly
            value = kwargs[self.name]

        elif "default" in self.argparse_kwargs:
            # We try to get the default value if posible
            default_value = self.argparse_kwargs["default"]
            value = default_value() if callable(default_value) else default_value

        else:
            raise MissingParameterError(self, name)

        # Convert the value to the desired type
        try:
            kwargs[get_value(self.name)] = self.convert(value)
        except ValueError as error:
            # Wrap value error in an Invalid cast error for
            # a more precise error message
            raise InvalidCastError(error, self, name)
        return kwargs


class StringParameter(Parameter):
    """Convert a string parameter to a string"""
    cast = str

class IntegerParameter(Parameter):
    """Convert an integer parameter to a int"""
    cast = int

class BoolParameter(Parameter):
    """Convert a bool parameter to a bool (includes yes, on, off)"""

    @staticmethod
    def cast(value):
        "Cast a bool value and accept false, no and off"
        if isinstance(value, str) and value.lower() in ["false", "no", "off"]:
            return False
        else:
            return bool(value)

class ListParameter(Parameter):
    """Convert a string separated with comma to a list"""

    @staticmethod
    def cast(value):
        "Transform a string into a list"
        if isinstance(value, list):
            # Already casted
            return value
        return str(value).split(",")

class FileParameter(Parameter):
    """Ensures that a file exists and opens it"""

    def __init__(self, name, mode='r', *args, **argparse_kwargs):
        self.file_mode = mode
        super().__init__(name, *args, **argparse_kwargs)

    def convert(self, value):
        try:
            return open(value, mode=self.file_mode)
        except FileNotFoundError:
            raise ValueError("Couldn't open %s (File not found)" % (value))
        except PermissionError:
            raise ValueError("Couldn't open %s (Permission error)" % (value))


class ChoiceParameter(Parameter):
    """Ensures that a parameter is an available choice"""

    def __init__(self, choices=None, *args, **argparse_kwargs):
        self.choices = choices
        argparse_kwargs["choices"] = self.choices
        super().__init__(*args, **argparse_kwargs)

    def convert(self, value):
        if value in self.choices:
            return super().convert(value)
        else:
            raise ValueError("%s is not an available choice" % value)

class NamespaceParameter(Parameter):
    """Parameter that returns all the values associated to a namespace"""

    def __init__(self, *args, **argparse_kwargs):
        super().__init__(*args, **argparse_kwargs)
        self.is_cli = False

    def parse(self, kwargs, name=None):
        "Returns a dict populated with all values of kwargs"

        kwargs = kwargs.copy()
        values = {}

        for key in kwargs:
            if self.name == get_namespace(key):
                values[get_value(key)] = kwargs[key]

        kwargs[self.name] = values
        return kwargs


def argparser_arguments(parameter, default_values=None):
    """Transform parameter into an argparser argument and adds it"""
    args = []
    kwargs = parameter.argparse_kwargs.copy()

    short = kwargs.pop("short", None)
    if short:
        args.append("-%s" % short)
    args.append("--%s" % get_value(parameter.name))

    # Allows external source of overriding default values
    if default_values and parameter.name in default_values:
        kwargs["default"] = default_values[parameter.name]


    kwargs.update({
        "dest": parameter.name
    })

    if isinstance(parameter, BoolParameter):
        kwargs["action"] = "store_true"
        kwargs["default"] = kwargs.get("default", False)

    if not "default" in kwargs:
        kwargs["required"] = True

    return (args, kwargs) if parameter.is_cli else (None, None)

#-- Alias for decorators
param = Parameter
string = StringParameter
integer = IntegerParameter
boolean = BoolParameter
choice = ChoiceParameter
array = ListParameter
namespace = NamespaceParameter
file = FileParameter

#-- Public function
def add_arguments(parser, default_values=None):
    """Transform an argparser based on the loaded classes"""
    for parameter in ARGPARSE_PARAMETERS:
        args, kwargs = argparser_arguments(parameter, default_values)
        if args:
            parser.add_argument(*args, **kwargs)
    return parser
