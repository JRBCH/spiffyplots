"""Top-level package for SpiffyPlots."""

__author__ = """Julian Rossbroich"""
__email__ = "julian.rossbroich@fmi.ch"
__version__ = "0.6.1"

from .lineplots import multiline
from .multipanel import MultiPanel

__all__ = ["MultiPanel", "multiline"]
