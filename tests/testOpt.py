import unittest

import params

class TestNamespace(unittest.TestCase):
    """Test the namespace decorator"""
    def test_name(self):
        """Ensure that we can use the namespace decorator with the name argument"""
        cls = type('X', (object,), dict(a=1))
        cls = params.namespace("test")(cls)
        self.assertEqual(cls._namespace, "test")

    def test_auto_name(self):
        """Ensure that the auto-naming function works properly"""
        cls = type('XExtension', (object,), dict(a=1))
        cls = params.namespace()(cls)
        self.assertEqual(cls._namespace, "X")

    def test_auto_name_no_extension(self):
        """Ensure that the auto-naming function works properly even when there is no Extension"""
        cls = type('XExtens', (object,), dict(a=1))
        cls = params.namespace()(cls)
        self.assertEqual(cls._namespace, "XExtens")


class TestParamArg(unittest.TestCase):
    """Test the params decorators"""

    def setUp(self):
        self.cls = type('X', (object,), dict(a=1))

    def test_params(self):
        """Ensure that the decorator param create a Parameter object on the type"""
        cls = params.string("test")(self.cls)
        self.assertEqual(len(cls._params), 1)

    def test_multi_params(self):
        """Ensure that classes are not stored internally in double"""
        cls = params.string("test")(self.cls)
        cls = params.string("test2")(cls)
        self.assertEqual(len(params.PARAMETERIZED_CLS), 1)


class CastTest(unittest.TestCase):
    """Test the casting of values in different types"""

    def test_convert_str(self):
        """Test that we can create a parameter that cast to string"""
        param = params.StringParameter(None, "test")
        self.assertEqual(param.convert("test"), "test")

    def test_convert_int(self):
        """Test that we can create a parameter that cast to int"""
        param = params.IntegerParameter(None, "test")
        self.assertEqual(param.convert("1"), 1)
        self.assertEqual(param.convert(2), 2)

    def test_convert_bool(self):
        """Test that we can create a parameter that cast to bool"""
        param = params.BoolParameter(None, "test")
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
        param = params.ChoiceParameter(cls=None, choices=["choice1", "choice2"],  name="test")
        self.assertEqual(param.convert("choice1"), "choice1")

    def test_convert_not_in_choices(self):
        """Ensure that input not in choice raises an error"""
        param = params.ChoiceParameter(cls=None, choices=["choice1", "choice2"], name="test")
        with self.assertRaises(ValueError):
            param.convert("notinchoice")


class TestParseParameter(unittest.TestCase):
    """Test the parsing of value via parameters"""

    def setUp(self):
        self.cls = type('X', (object,), dict(a=1))

    def test_parse_str(self):
        """Ensure that we can do a simple parse via a parameter"""
        param = params.Parameter(self.cls, "test")
        parsed_kwargs = param.parse({"test":"value"})
        self.assertIn("test", parsed_kwargs)
        self.assertEqual(parsed_kwargs["test"], "value")

    def test_parse_multi_parameters(self):
        """Ensure that other parameters are not lost"""
        param = params.Parameter(self.cls, "test")
        parsed_kwargs = param.parse({"test": "value", "doNotDelete": True})
        self.assertEqual(parsed_kwargs["doNotDelete"], True)

    def test_missing_value(self):
        """Ensure an error is raised on missing parameterError"""
        param = params.Parameter(self.cls, "test")
        with self.assertRaises(params.MissingParameterError):
            param.parse({"test2":"value"})

    def test_default_parse(self):
        """Ensure that the default is loaded when missing parameter"""
        param = params.Parameter(self.cls, "test", default="default_value")
        parsed_kwargs = param.parse({})
        self.assertEqual(parsed_kwargs["test"], "default_value")

    def test_none(self):
        """Ensure that explicit none get assigned"""
        param = params.Parameter(self.cls, "test")
        parsed_kwargs = param.parse({"test":None})
        self.assertEqual(parsed_kwargs["test"], None)

    def test_default_none(self):
        """Ensure that explicit default none get assigned"""
        param = params.Parameter(self.cls, "test", default=None)
        parsed_kwargs = param.parse({})
        self.assertEqual(parsed_kwargs["test"], None)

class TempParentClass(object):
    """Test class object to test the replace init function"""
    def __init__(self, value=None, original=None, **kwargs):
        self.value = value
        self.original = original

class ReplaceInitTest(unittest.TestCase):
    def setUp(self):
        self.cls = type('TempClass', (TempParentClass,), dict(a=1))
        self.cls._params = []

    def test_replace_init(self):
        """Ensure that the replace_init function doesn't overshadow"""
        self.cls._params.append(params.Parameter(self.cls, "value"))
        params.param.replace_init(self.cls)
        instance = self.cls(**{"value":"abc"})
        self.assertEqual(instance.value, "abc")

    def test_replace_init_exception(self):
        """Ensure that the replace_init raises missing parameter error"""
        self.cls._params.append(params.Parameter(self.cls, "value"))
        params.param.replace_init(self.cls)
        with self.assertRaises(params.MissingParameterError):
            instance = self.cls()

    def test_replace_init_missing_namespace(self):
        """Ensure that the replace_init raises missing namespace error"""
        self.cls._params.append(params.Parameter(self.cls, "value"))
        self.cls._namespace = "test"
        params.param.replace_init(self.cls)
        with self.assertRaises(params.MissingNamespaceError):
            instance = self.cls({})

    def test_replace_init_namespace(self):
        """Ensure that the replace_init auto loads from namespace"""
        self.cls._params.append(params.Parameter(self.cls, "value"))
        self.cls._namespace = "test"
        params.param.replace_init(self.cls)
        instance = self.cls(**{"test":{"value":"abc"}})
        self.assertEqual(instance.value, "abc")

    def test_replace_init_namespace_original(self):
        """Ensure that the replace_init keeps other namespaces"""
        self.cls._params.append(params.Parameter(self.cls, "value"))
        self.cls._namespace = "test"
        params.param.replace_init(self.cls)
        instance = self.cls(**{"test":{"value":"abc"}, "original":{"nb":2}})
        self.assertEqual(instance.original, {"nb":2})

import argparse

class ArgParseTest(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.cls = type('TempClass', (TempParentClass,), dict(a=1))
        self.cls._params = []

    def test_argparser_single(self):
        """Test on a single parameter added to the argparser"""
        param = params.Parameter(None, "test")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "value"]))
        self.assertEqual(args["test"], "value")

    def test_argparser_multiple(self):
        """Ensure the argparser current parameter don't get deleted"""
        param = params.Parameter(None, "test")
        self.parser.add_argument("--noop")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "value", "--noop", "true"]))
        self.assertEqual(args["noop"], "true")

    def test_short_argument(self):
        """Ensure that we can configure parameter that takes short arg"""
        param = params.Parameter(None, "test", short="a")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["-a", "value"]))
        self.assertEqual(args["test"], "value")

    def test_argparser_namespace(self):
        """Ensure the parameter gets put into the right namespace"""
        param = params.Parameter(None, "test", short="a", namespace="foo")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "value"]))
        self.assertEqual(args["foo"]["test"], "value")

    def test_argparser_convert_str(self):
        """Ensure the argparser are in the string format"""
        param = params.StringParameter(None, "test")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "2"]))
        self.assertEqual(args["test"], "2")

    def test_argparser_convert_bool(self):
        """Ensure the argparser are in the bool format"""
        param = params.BoolParameter(None, "test")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "False"]))
        self.assertEqual(args["test"], False)

    def test_argparser_convert_int(self):
        """Ensure the argparser are in the int format"""
        param = params.IntegerParameter(None, "test")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "2"]))
        self.assertEqual(args["test"], 2)

    def test_argparser_convert_choice(self):
        """Ensure the argparser work with the choices"""
        param = params.ChoiceParameter(["valid"], None, "test")
        param.to_argparser(self.parser)
        args = vars(self.parser.parse_args(["--test", "valid"]))
        self.assertEqual(args["test"], "valid")
