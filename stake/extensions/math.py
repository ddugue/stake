
import os

from stake import params
from . import base
from .. import logging

class MathExtension(base.Extension):
    """ Provides functions to work with numbers """
    @staticmethod
    def sum(values, accessor=None):
        "Return sum of values, if accessor, sum accessed values"
        return 0

    def get_context_data(self) -> dict:
        "Extends the context data with some math fn"
        ctxt_data = super().get_context_data()
        ctxt_data["int"] = int
        ctxt_data["sum"] = self.sum
        return ctxt_data


__default__ = MathExtension
