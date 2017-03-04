import argparse

class StoreNamespace(argparse.Action):
    """argparse action to store into a sub dictionnary a variable"""

    def __init__(self, option_strings, dest, namespace=None, **kwargs):
        if namespace is None:
            raise ValueError("Namespace name must be provided")
        self.namespace = namespace
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        subnamespace = getattr(namespace, self.namespace, {})
        subnamespace[self.dest] = values
        setattr(namespace, self.namespace, subnamespace)

def recursive_update(dictionnary, new_dictionnary):
    """Recursively update a dictionary object and its sub-dictionaries"""
    for k,v in new_dictionnary.items():
        if isinstance(v, dict):
            dictionnary[k] = recursive_update(dictionnary.get(k, {}), v)
        elif isinstance(v, list):
            dictionnary.get(k, []).extend(v)
        else:
            dictionnary[k] = v
    return dictionnary

def pipe(iterator, fn, init=None):
    """Pipe an object into a function of each iteration"""
    for obj in iterator:
        init = getattr(obj, fn)(init)
    return init
