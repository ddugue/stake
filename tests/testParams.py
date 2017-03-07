import unittest
import argparse
import params

class TestParamArg(unittest.TestCase):
    """Test the params decorators"""

    def setUp(self):
        self.cls = type('X', (object,), dict(a=1))
        params.ARGPARSE_PARAMETERS = set()

    def test_params(self):
        """Ensure that the decorator param create a Parameter object on the type"""
        cls = params.string("test")(self.cls)
        self.assertEqual(len(params.ARGPARSE_PARAMETERS), 1)

    def test_multi_params(self):
        """Ensure that classes are not stored internally in double"""
        cls = params.string("test")(self.cls)
        cls = params.string("test2")(cls)
        self.assertEqual(len(params.ARGPARSE_PARAMETERS), 2)


class CastTest(unittest.TestCase):
    """Test the casting of values in different types"""

    def test_convert_str(self):
        """Test that we can create a parameter that cast to string"""
        param = params.StringParameter("test")
        self.assertEqual(param.convert("test"), "test")

    def test_convert_int(self):
        """Test that we can create a parameter that cast to int"""
        param = params.IntegerParameter("test")
        self.assertEqual(param.convert("1"), 1)
        self.assertEqual(param.convert(2), 2)

    def test_convert_bool(self):
        """Test that we can create a parameter that cast to bool"""
        param = params.BoolParameter("test")
        self.assertEqual(param.convert("true"), True)
        self.assertEqual(param.convert("on"), True)
        self.assertEqual(param.convert("yes"), True)
        self.assertEqual(param.convert("True"), True)
        self.assertEqual(param.convert("false"), False)
        self.assertEqual(param.convert("no"), False)
        self.assertEqual(param.convert("off"), False)
        self.assertEqual(param.convert("False"), False)
        self.assertEqual(param.convert(0), False)
        self.assertEqual(param.convert(1), True)
        self.assertEqual(param.convert(True), True)
        self.assertEqual(param.convert(False), False)


    def test_convert_choices(self):
        """Test that we can create a parameter that cast from a list"""
        param = params.ChoiceParameter(choices=["choice1", "choice2"],  name="test")
        self.assertEqual(param.convert("choice1"), "choice1")

    def test_list(self):
        "Test that we can convert separated string with commas to a list"
        param = params.ListParameter(name="test")
        self.assertEqual(param.convert("dav,dav"), ["dav","dav"])
        self.assertEqual(param.convert("dav"), ["dav"])

    def test_convert_not_in_choices(self):
        """Ensure that input not in choice raises an error"""
        param = params.ChoiceParameter(choices=["choice1", "choice2"], name="test")
        with self.assertRaises(ValueError):
            param.convert("notinchoice")


class TestParseParameter(unittest.TestCase):
    """Test the parsing of value via parameters"""

    def setUp(self):
        self.cls = type('X', (object,), dict(a=1))

    def test_parse_str(self):
        """Ensure that we can do a simple parse via a parameter"""
        param = params.Parameter("test")
        parsed_kwargs = param.parse({"test":"value"})
        self.assertIn("test", parsed_kwargs)
        self.assertEqual(parsed_kwargs["test"], "value")

    def test_parse_multi_parameters(self):
        """Ensure that other parameters are not lost"""
        param = params.Parameter("test")
        parsed_kwargs = param.parse({"test": "value", "doNotDelete": True})
        self.assertEqual(parsed_kwargs["doNotDelete"], True)

    def test_missing_value(self):
        """Ensure an error is raised on missing parameterError"""
        param = params.Parameter("test")
        with self.assertRaises(params.MissingParameterError):
            param.parse({"test2":"value"})

    def test_default_parse(self):
        """Ensure that the default is loaded when missing parameter"""
        param = params.Parameter("test", default="default_value")
        parsed_kwargs = param.parse({})
        self.assertEqual(parsed_kwargs["test"], "default_value")

    def test_none(self):
        """Ensure that explicit none get assigned"""
        param = params.Parameter("test")
        parsed_kwargs = param.parse({"test" : None})
        self.assertEqual(parsed_kwargs["test"], None)

    def test_default_none(self):
        """Ensure that explicit default none get assigned"""
        param = params.Parameter("test", default=None)
        parsed_kwargs = param.parse({})
        self.assertEqual(parsed_kwargs["test"], None)

#-- Testing class
class TempParentClass:
    """Test class object to test the replace init function"""
    def __init__(self, value=None, original=None, **kwargs):
        self.value = value
        self.original = original

    def sub_fn(self, value=None, **kwargs):
        "Test function to see if decorator works on class members"
        return value


def temp_fn(value, **kwargs):
    "Test function to see if decorator works on module-level function"
    return value


class ReplaceInitTest(unittest.TestCase):
    "Ensures that the decorators work on all kinds of Python objects"

    def setUp(self):
        self.cls = type('TempClass', (TempParentClass,), dict(a=1))

    def test_replace_init(self):
        """Ensure that the replace_init function doesn't overshadow"""

        self.cls = params.Parameter("value")(self.cls)
        instance = self.cls(**{"value":"abc"})
        self.assertEqual(instance.value, "abc")

    def test_replace_init_exception(self):
        """Ensure that the replace_init raises missing parameter error"""
        self.cls = params.Parameter("value")(self.cls)
        with self.assertRaises(params.MissingParameterError):
            instance = self.cls()

    def test_replace_sub_fn(self):
        "Ensures that the decorator works with class members"
        self.cls.sub_fn = params.Parameter("value", default=2)(self.cls.sub_fn)
        instance = self.cls()
        self.assertEqual(instance.sub_fn(),2)

    def test_replace_fn(self):
        "Ensures that the decorator works with functions"
        fn = params.Parameter("value", default=2)(temp_fn)
        self.assertEqual(fn(), 2)


class ArgParseTest(unittest.TestCase):
    "Ensures that argparsing works correctly with parameters"

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.cls = type('TempClass', (TempParentClass,), dict(a=1))
        params.ARGPARSE_PARAMETERS = set()

    def test_argparser_single(self):
        """Test on a single parameter added to the argparser"""
        param = params.StringParameter("test")
        params.add_arguments(self.parser)
        args = vars(self.parser.parse_args(["--test", "value"]))
        self.assertEqual(args["test"], "value")

    def test_argparser_multiple(self):
        """Ensure the argparser current parameter don't get deleted"""
        param = params.StringParameter("test")
        self.parser.add_argument("--noop")
        params.add_arguments(self.parser)
        args = vars(self.parser.parse_args(["--test", "value", "--noop", "true"]))
        self.assertEqual(args["noop"], "true")

    def test_short_argument(self):
        """Ensure that we can configure parameter that takes short arg"""
        param = params.StringParameter("test", short="a")
        params.add_arguments(self.parser)
        try:
            args = vars(self.parser.parse_args(["-a", "value"]))
        except SystemExit as error:
            print(error.args)
        self.assertEqual(args["test"], "value")

    def test_argparser_convert_choice(self):
        """Ensure the argparser work with the choices"""
        param = params.ChoiceParameter(["valid"], "test")
        params.add_arguments(self.parser)
        args = vars(self.parser.parse_args(["--test", "valid"]))
        self.assertEqual(args["test"], "valid")
