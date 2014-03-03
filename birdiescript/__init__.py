# -*- coding: utf-8 -*-
"""Birdiescript reference implementation.

Documentation goes here.
"""

from __future__ import (absolute_import, division, generators, nested_scopes,
	print_function, unicode_literals, with_statement)

from .__version__ import *
from .core import *
from .builtins import *

__author__ = 'Remy Oukaour'
__copyright__ = 'Copyright 2014 Remy Oukaour.'
__license__ = 'MIT/X11'
__version__ = version

__all__ = ['__author__', '__copyright__', '__license__', '__version__',
	'BirdieCoercionError', 'BirdieType', 'BirdieNumber', 'BirdieInt',
	'BirdieFloat', 'BirdieComplex', 'BirdieSequence', 'BirdieList',
	'BirdieString', 'BirdieRegex', 'BirdieCallable', 'BirdieBlock',
	'BirdieBuiltin', 'parse_int', 'parse_complex', 'parse_chars',
	'parse_string', 'parse_regex', 'parse_name', 'BirdieToken',
	'BirdieTypeError', 'BirdieContext', 'builtins', 'using_regex_module',
	'predefine_variables', 'execute_file', 'repl_environment']
