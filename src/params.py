#-- Imports
import copy
import warnings

from utils import *

#-- Constants
PARAMETERIZED_CLS = set()

#-- Exceptions
class MissingNamespaceError(Exception):
    """Triggered when missing a namespace upon initialization"""

    def __init__(self, cls, namespace, *args, **kwargs):
        self.namespace = namespace
        self.cls = cls
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s is missing for %s, make sure to provide the arguments " \
            + "as keyword arguments" \
            % (self.namespace, self.cls.__name__)

class ParsingError(Exception):
    """Error triggered when there is a parser error"""

    def __init__(self, parameter, *args, **kwargs):
        self.parameter = parameter
        super().__init__(*args, **kwargs)

class MissingParameterError(ParsingError):
    """Triggered when there's a missing parameter upon initialization"""

    def __str__(self):
        return "%s is missing for %s, make sure to either add " \
            + "a default value for the parameter or provide its value" \
            % (self.parameter.name, self.parameter.cls.__name__)

class InvalidCastError(ParsingError):
    """Triggered when there's an invalid type casting upon initialization"""

    def __init__(self, value_error, *args, **kwargs):
        self.value_error = value_error
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s could not be cast with %s on %s: %s" \
            % (
                self.parameter.name,
                repr(self.parameter.cast),
                self.parameter.cls.__name__,
                self.value_error.message
            )


#-- Classes
class Parameter(object):
    """Handles the representation of a configuration parameter"""

    def __init__(self, cls, name, short="", is_cli=True, *args, **argparse):
        # Associated class object
        self.cls = cls

        # Name of the parameter
        self.name = name

        # Short version of the parameter (for argparse)
        assert len(short) < 2
        self.short = short
        self.is_cli = is_cli
        if self.short and not self.is_cli:
            warnings.warn("Providing short argument and not using argparse is inconsitant")

        # Namespace (plugin space) of the parameter
        self.namespace = argparse.pop("namespace", "")

        # Args to pass to argparse
        self.args = argparse

    def get_cast(self):
        """Return function to cast values"""
        return getattr(self, "cast", lambda x:x)

    def convert(self, value):
        """Cast the value to the desired type, raise value error on impossible cast"""
        return self.get_cast()(value)

    def parse(self, kwargs):
        """Change parameter object value for this parameter on kwargs"""

        if self.name in kwargs:
            # We try first to get the value directly
            value = kwargs[self.name]
        elif "default" in self.args:
            # We try to get the default value if posible
            def_value = self.args["default"]
            value = def_value() if callable(def_value) else def_value
        else:
            # Missing parameter
            raise MissingParameterError(self)

        # Convert the value to the desired type
        try:
            kwargs[self.name] = self.convert(value)
        except ValueError as ex:
            # Wrap value error in an Invalid cast error for
            # a more precise error message
            raise InvalidCastError(ex, self)
        return kwargs


    def get_argparser_kwargs(self):
        """Get the arguments to pass to argparser.add_argument"""

        kwargs = copy.deepcopy(self.args)
        kwargs.update({
            "dest": self.name,
            "type": self.get_cast(),
            "required": True
        })

        if "default" in kwargs:
            del kwargs["required"]


        namespace = self.namespace or getattr(self.cls, "_namespace", None)
        if namespace:
            kwargs["action"] = StoreNamespace
            kwargs["namespace"] = self.namespace
        return kwargs

    def to_argparser(self, argparser):
        """Transform parameter into an argparser argument and adds it"""
        if self.is_cli:
            args = []
            if self.short:
                args.append("-%s" % self.short)
            args.append("--%s" % self.name)
            argparser.add_argument(*args, **self.get_argparser_kwargs())
        return argparser

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
        if isinstance(value, str) and \
           value.lower() in ["false", "no", "off"]:
            return False
        else:
            return bool(value)


class ChoiceParameter(Parameter):
    """Ensures that a parameter is an available choice"""

    def __init__(self, choices=None, *args, **kwargs):
        self.choices = choices
        super().__init__(*args, **kwargs)

    def get_argparser_kwargs(self):
        """Forces arguments sent via argpraser to be bool"""
        kwargs = super().get_argparser_kwargs()
        kwargs["choices"] = self.choices
        return kwargs

    def convert(self, value):
        if value in self.choices:
            return super().convert(value)
        else:
            raise ValueError("%s is not an available choice" % value)

#-- Decorators
class namespace():
    """Encapsulate all parameter type inside a namespace

    If you do not provide a name, the auto-generated name
    for the namespace will be the class name minus the 'Extension' suffix"""

    def __init__(self, name=""):
        self.name = name

    def __call__(self, cls):
        cls._namespace = self.name or cls.__name__.replace("Extension", "")
        return cls

class param():
    """Encapsulate object initialization with a string parameter"""
    parameter_type = Parameter

    @staticmethod
    def replace_init(cls):
        # Override init to add parameter verification and raise error
        original_init = cls.__init__

        def validate(self, *args, **kwargs):
            namespace = getattr(self.__class__, "_namespace", None)

            if namespace and namespace not in kwargs:
                raise MissingNamespaceError(self.__class__, namespace=namespace)

            kwargs = copy.deepcopy(kwargs)
            kwargs.update(kwargs.get(namespace,{}))
            kwargs = pipe(self.__class__._params, "parse", kwargs)

            original_init(self, *args, **kwargs)

        cls.__init__ = validate


    def get_parameter_type(self):
        """Return the parameter type"""
        return self.parameter_type

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls):
        if not hasattr(cls, "_params"):
            cls._params = []

        # We proxy decorators argument to the
        # Parameter class (see above)
        cls._params.append(self.get_parameter_type()(cls, *self.args, **self.kwargs))

        # We inject a new __init__ function that will trigger
        # validation errors
        param.replace_init(cls)

        # We add the class to the CLS singleton to retrieve
        # it to generate the argparser
        PARAMETERIZED_CLS.add(cls)
        return cls

class string(param):
    """Encapsulate object initialization with a string parameter"""
    parameter_type = StringParameter

class integer(param):
    """Encapsulate object initialization with an integer parameter"""
    parameter_type = IntegerParameter
    # TODO: Handle max and min value

class boolean(param):
    """Encapsulate object initialization with an integer parameter"""
    parameter_type = BoolParameter

class choice(param):
    """Encapsulate object initialization with restricted choice parameter"""
    parameter_type = ChoiceParameter


class datetime(param):
    # TODO:
    pass

class list(param):
    # TODO:
    pass


#-- Public function
def to_argparser(parser):
    """Transform an argparser based on the loaded classes"""
    for cls in PARAMETERIZED_CLS:
        parser = pipe(cls._params, "to_argparser", parser)
    return parser


