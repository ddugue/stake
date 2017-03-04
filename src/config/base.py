from argparse import ArgumentParser

class ConfigParser():
    """Abstract parsing class to extract configuration from any source"""

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)



