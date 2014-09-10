# -*- coding: utf-8 -*-
"""
Birdiescript interpreter and REPL environment.

Documentation goes here.
"""


#################### Imports ####################

from __future__ import (absolute_import, division, generators, nested_scopes,
	print_function, unicode_literals, with_statement)

import sys         # version_info, maxunicode, exit, stdin, stdout,
import math        # frexp                  getrecursionlimit, setrecursionlimit
import cmath       # isinf, isnan
import collections # Mapping, Iterable, Counter
import functools   # reduce
import types       # MethodType, wraps
import copy        # copy
import time        # sleep, clock, time, gmtime, localtime, strftime, strptime,
import traceback   # print_exc                                  timezone, tzname
import codecs      # open
import argparse    # ArgumentParser
import platform    # python_version

# Python in Cygwin dumps core upon exiting if imports are placed in builtins.py.
import itertools   # permutations
import random      # seed, random, randrange
import datetime    # datetime
import calendar    # timegm, day_name, day_abbr, month_name, month_abbr
import struct      # pack, unpack
import os          # environ
import subprocess  # check_output
import shlex       # split

try:
	import dateutil.relativedelta as relativedelta # relativedelta
except ImportError:
	relativedelta = None

try:
	import urllib2 as urllib        # urlopen
except ImportError:
	import urllib.request as urllib # urlopen

try:
	import regex
	using_regex_module = True
	lower_rx = r'\p{Ll}'
except ImportError:
	import re as regex
	using_regex_module = False
	regex.A = regex.ASCII = 0
	regex.B = regex.BESTMATCH = 0
	regex.E = regex.ENHANCEMATCH = 0
	regex.F = regex.FULLCASE = 0
	regex.R = regex.REVERSE = 0
	regex.W = regex.WORD = 0
	regex.V0 = regex.VERSION0 = 0
	regex.V1 = regex.VERSION1 = 0
	regex.DEFAULT_VERSION = regex.VERSION0
	lower_rx = 'a-zß-öø-ÿάώа-џａ-ｚ' # Most common lowercase letters

try:
	import readline
except ImportError:
	readline = None

from .__version__ import version
from . import colors

HEADER_COLORS = colors.FG_MAGENTA | colors.FG_BOLD
SUBHEADER_COLORS = colors.FG_MAGENTA | colors.FG_NOBOLD
STACK_COLORS = colors.FG_GREEN | colors.FG_NOBOLD
VALUE_COLORS = colors.FG_CYAN | colors.FG_BOLD
INFO_COLORS = colors.FG_YELLOW | colors.FG_BOLD
NOTE_COLORS = colors.FG_GREY | colors.FG_NOBOLD
ALERT_COLORS = colors.FG_RED | colors.FG_BOLD


#################### Utility functions ####################

if sys.version_info.major <= 2:
	# Python 2
	str = unicode
	chr = unichr
	input = raw_input
	
	# Hide 'exec code in ns' statement from Python 3
	eval(compile("""def exec_python(code, gns, lns):
		exec compile(code, '<birdiescript>', 'exec') in gns, lns
		""", '<exec_python>', 'exec'))
	
	def safe_string(s):
		"""Hack to avoid UnicodeDecodeErrors in Python 2 and 3."""
		c = sys.stdout.encoding or 'cp437'
		return str(s).encode(c, 'backslashreplace')
else:
	# Python 3
	long = int
	reduce = functools.reduce
	
	def safe_string(s):
		"""Hack to avoid UnicodeDecodeErrors in Python 2 and 3."""
		c = sys.stdout.encoding or 'cp437'
		return str(s).encode(c, 'backslashreplace').decode(c)
	
	def exec_python(code, gns, lns):
		exec(compile(code, '<birdiescript>', 'exec'), gns, lns)

class Sentinel(object):
	"""A unique object with a meaningful string representation."""
	
	def __init__(self, name):
		self.name = name
	
	def __repr__(self):
		return '{}({})'.format(self.__class__.__name, repr(self.name))
	
	def str(self):
		return self.name

def identity(x):
	"""Return the argument."""
	return x

def is_integral(x):
	"""Return whether the argument is equal to its integer part."""
	if isinstance(x, complex):
		if x.imag:
			return False
		x = x.real
	return not cmath.isinf(x) and not cmath.isnan(x) and x == int(x)

def escape_birdiescript(s):
	"""Escape a Birdiescript string."""
	return s.replace('\\', '\\\\').replace('`', '\\`')

def nice_float(x):
	"""
	Return a short string representation of a floating point number.
	
	Taken from the python-nicefloat module <http://labix.org/python-nicefloat>,
	which is based on the paper "Printing Floating-Point Numbers Quickly and
	Accurately" by Robert G. Burger and R. Kent Dybvig.
	"""
	# Special cases for 0, infinity, and NaN
	if not x:
		return '0.'
	if cmath.isinf(x):
		if x < 0:
			return '-Inf'
		return 'Inf'
	if cmath.isnan(x):
		return 'Nan'
	# Copied from http://labix.org/python-nicefloat
	f, e = math.frexp(x)
	if x < 0:
		f = -f
	f = int(f * 2**53)
	e -= 53
	if e >= 0:
		be = 2**e
		if f != 2**52:
			r, s, mp, mm = f*be*2, 2, be, be
		else:
			be1 = be*2
			r, s, mp, mm = f*be1*2, 4, be1, be
	elif e == -1074 or f != 2**52:
		r, s, mp, mm = f*2, 2**(1-e), 1, 1
	else:
		r, s, mp, mm = f*4, 2**(2-e), 2, 1
	k = 0
	round = f % 2 == 0
	while not round and r+mp*10 <= s or r+mp*10 < s:
		r *= 10
		mp *= 10
		mm *= 10
		k -= 1
	while round and r+mp >= s or r+mp > s:
		s *= 10
		k += 1
	l = []
	while True:
		d, r = divmod(r*10, s)
		d = int(d)
		mp *= 10
		mm *= 10
		tc1 = round and r == mm or r < mm
		tc2 = round and r+mp == s or r+mp > s
		if not tc1:
			if not tc2:
				l.append(d)
				continue
			l.append(d+1)
		elif not tc2 or r*2 < s:
			l.append(d)
		else:
			l.append(d+1)
		break
	if k <= 0:
		l.insert(0, '0' * abs(k))
		l.insert(0, '.')
	elif k < len(l):
		l.insert(k, '.')
	else:
		l.append('0' * (k - len(l)))
		l.append('.')
	n = ''.join(map(str, l))
	# Further shorten the string using scientific notation
	if n.startswith('.000'):
		n = n[1:]
		p = 0
		while n.startswith('0'):
			n = n[1:]
			p -= 1
		n1 = (n[0] + '.' + n[1:] + 'e' + str(p-1)).replace('.e', 'e')
		n2 = n + 'e' + str(p-len(n))
		n = n2 if len(n2) < len(n1) else n1
	elif n.endswith('00.'):
		n = n[:-1]
		p = 0
		while n.endswith('0'):
			n = n[:-1]
			p += 1
		n = n + 'e' + str(p)
	if x < 0:
		n = '-' + n
	return n


#################### Birdiescript exceptions ####################

class BTypeError(TypeError):
	
	def __init__(self, op, args):
		if isinstance(args, (tuple, list)):
			types = tuple(a.__class__.__name__ for a in args)
		else:
			types = args.__class__.__name__
		msg = 'cannot apply {} to {}: {}'.format(repr(op),
			repr(types), repr(args))
		super(TypeError, self).__init__(msg)

class BCoercionError(TypeError):
	
	def __init__(self, a, b):
		msg = 'cannot coerce {} to {}: {}'.format(
			repr(a.__class__.__name__),
			repr(b.__class__.__name__), repr(a))
		super(TypeError, self).__init__(msg)


#################### Birdiescript types ####################

class BType(object):
	"""Base class for all Birdiescript value types."""
	
	rank = -1
	
	@staticmethod
	def commonize(a, b):
		"""Return the arguments coerced to a common type."""
		return (a.coerce(b), b.coerce(a))
	
	@staticmethod
	def from_python(value):
		"""Return the Birdiescript equivalent of a Python value."""
		if isinstance(value, BType):
			return value
		elif isinstance(value, (int, long)):
			return BInt(value)
		elif isinstance(value, float):
			return BFloat(value)
		elif isinstance(value, complex):
			return BComplex(value)
		elif isinstance(value, str):
			return BStr(value)
		elif isinstance(value, type(regex.compile(''))):
			return BRegex(value)
		elif isinstance(value, collections.Mapping):
			return BList([BList([BType.from_python(k),
				BType.from_python(v)]) for (k, v) in
				value.items()])
		elif isinstance(value, collections.Iterable):
			return BList([BType.from_python(v) for v in value])
		else:
			return BStr(str(value))
	
	def __init__(self, value):
		self.value = value
	
	def __repr__(self):
		return safe_string(repr(self.value))
	
	def __str__(self):
		return str(self.value)
	
	def __eq__(self, other):
		return self.simplify().value == other.simplify().value
	
	def __ne__(self, other):
		return not (self == other)
	
	def __lt__(self, other):
		return self.simplify().value < other.simplify().value
	
	def __nonzero__(self):
		return bool(self.value)
	
	def __bool__(self):
		return self.__nonzero__()
	
	def __hash__(self):
		return hash(self.value)
	
	def format_value(self):
		"""Return the format string value for this Birdiescript value."""
		return self.value
	
	def python_value(self):
		"""Return the Python equivalent of this Birdiescript value."""
		return self.value
	
	def tokenize(self):
		"""
		Return a list of BToken instances that, when executed,
		evaluate to this value.
		"""
		return BContext.tokenized(repr(self))
	
	def simplify(self):
		"""Return the simplest value equivalent to this value."""
		return self
	
	def coerce(self, other):
		"""
		Return this value coerced to the same type as the argument,
		if the argument's type ranks higher than its own.
		
		The type hierarchy is:
		int < float < complex < list < string < regex < block < builtin
		"""
		if other.rank < self.rank:
			return self
		return self.convert(other)
	
	def convert(self, other):
		"""Return this value converted to the same type as the argument."""
		msg = 'cannot convert abstract value: {}'.format(repr(self))
		raise NotYetImplemented(msg)
	
	def apply(self, context):
		"""
		Execute this value in the given context.
		
		Most values push themselves onto the stack. Blocks and builtins
		are functions and have more complicated effects.
		"""
		context.push(self)

class BNum(BType):
	"""Base class for all Birdiescript numeric types."""

class BReal(BNum):
	"""Base class for all Birdiescript real numeric types."""

class BInt(BReal):
	"""
	Birdiescript integer type.
	
	Uses arbitrary precision integers internally.
	"""
	
	rank = 0
	
	def __init__(self, value=0):
		self.value = int(value)
	
	def __repr__(self):
		"""
		Return the decimal or hexadecimal (with a leading 0)
		representation of this integer, whichever is shorter.
		"""
		base10 = repr(self.value).rstrip('Ll')
		base16 = '0' + hex(self.value)[2:].rstrip('Ll').lower()
		r = base16 if len(base16) < len(base10) else base10
		if r.startswith('-'):
			r = r[1:] + 'm'
		return r
	
	def __str__(self):
		"""Return the decimal representation of this integer."""
		return repr(self.value).rstrip('Ll')
	
	def convert(self, other):
		if isinstance(other, BNum):
			return type(other)(self.value)
		elif isinstance(other, BList):
			return BList([self])
		elif isinstance(other, BStr):
			if 0 <= self.value <= sys.maxunicode:
				return BStr(chr(self.value))
			return BStr(str(self))
		elif isinstance(other, BRegex):
			if 0 <= self.value <= sys.maxunicode:
				v = chr(self.value)
			else:
				v = str(self)
			return BRegex(regex.compile(v, other.value.flags))
		elif isinstance(other, BFunc):
			return BBlock(self.tokenize())
		else:
			raise BCoercionError(self, other)

class BFloat(BReal):
	"""
	Birdiescript floating point number type.
	
	Uses double precision IEE 754 floating point internally.
	"""
	
	rank = 1
	
	def __init__(self, value=0.0):
		self.value = float(value)
	
	def __repr__(self):
		r = nice_float(self.value)
		if r.startswith('-'):
			r = r[1:] + 'm'
		return r
	
	def __str__(self):
		return nice_float(self.value)
	
	def simplify(self):
		if is_integral(self.value):
			return BInt(self.value)
		return self
	
	def convert(self, other):
		if isinstance(other, BNum):
			return type(other)(self.value)
		elif isinstance(other, BList):
			return BList([self])
		elif isinstance(other, BStr):
			return BStr(str(self))
		elif isinstance(other, BRegex):
			return BRegex(regex.compile(str(self),
				other.value.flags))
		elif isinstance(other, BFunc):
			return BBlock(self.tokenize())
		else:
			raise BCoercionError(self, other)

class BComplex(BNum):
	"""Birdiescript complex number type."""
	
	rank = 2
	
	def __init__(self, value=0j):
		self.value = complex(value)
	
	def __repr__(self):
		real = nice_float(self.value.real)
		imag = nice_float(self.value.imag).rstrip('.') + 'j'
		if not self.value.imag:
			if real.startswith('-'):
				real = real[1:] + 'm'
			return real
		if not self.value.real:
			if imag.startswith('-'):
				imag = imag[1:] + 'm'
			return imag
		if imag.startswith('-'):
			imag = imag[1:] + 'm'
		if real.startswith('-'):
			return imag + real[1:].rstrip('.') + '-'
		return imag + real.rstrip('.') + '+'
	
	def __str__(self):
		real = nice_float(self.value.real).rstrip('.')
		imag = nice_float(self.value.imag).rstrip('.') + 'j'
		if not imag.startswith('-'):
			imag = '+' + imag
		return '(' + real + imag + ')'
	
	def simplify(self):
		if is_integral(self.value):
			return BInt(self.value.real)
		if not self.value.imag:
			return BFloat(self.value.real)
		return self
	
	def convert(self, other):
		if isinstance(other, BComplex):
			return self
		elif isinstance(other, BNum):
			return type(other)(self.simplify().value)
		elif isinstance(other, BList):
			return BList([self])
		elif isinstance(other, BStr):
			return BStr(str(self))
		elif isinstance(other, BRegex):
			return BRegex(regex.compile(str(self),
				other.value.flags))
		elif isinstance(other, BFunc):
			return BBlock(self.tokenize())
		else:
			raise BCoercionError(self, other)

class BSeq(BType):
	"""Base class for all Birdiescript sequential types."""

class BList(BSeq):
	"""Birdiescript list type."""
	
	rank = 3
	
	def __init__(self, value=None):
		self.value = list(value or [])
	
	def __repr__(self):
		return '[' + ' '.join(map(repr, self.value)) + ']'
	
	def __str__(self):
		return '[' + ' '.join(map(str, self.value)) + ']'
	
	def __hash__(self):
		return hash(repr(self))
	
	def format_value(self):
		return tuple(v.format_value() for v in self.value)
	
	def python_value(self):
		return [v.python_value() for v in self.value]
	
	def tokenize(self):
		tokens = [BToken('name', '[')]
		tokens += [v.tokenize() for v in self.value]
		tokens += [BToken('name', ']')]
		return tokens
	
	def convert(self, other):
		if isinstance(other, BList):
			return self
		elif isinstance(other, BStr):
			v = ''.join(str(v.convert(other)) for v in self.value)
			return BStr(v)
		elif isinstance(other, BRegex):
			v = ''.join(str(v.convert(other)) for v in self.value)
			return BRegex(regex.compile(v, other.value.flags))
		elif isinstance(other, BFunc):
			v = sum([v.tokenize() for v in self.value], [])
			return BBlock(v)
		else:
			raise BCoercionError(self, other)

class BChars(BSeq):
	"""Base class for all Birdiescript string-like types."""

class BStr(BChars):
	"""
	Birdiescript string type.
	
	Uses Unicode strings internally.
	"""
	
	rank = 4
	
	chars_string_rx = regex.compile(r'^.[{Ll}]*$'.format(Ll=lower_rx),
		regex.VERSION1 | regex.DOTALL)
	
	def __init__(self, value=None):
		self.value = str(value or '')
	
	def __repr__(self):
		if regex.match(BStr.chars_string_rx, self.value):
			return safe_string("'" + self.value)
		escaped = escape_birdiescript(self.value)
		return safe_string('`' + escaped + '`')
	
	def __str__(self):
		return self.value
	
	def format_value(self):
		return self
	
	def simplify(self):
		return BList(BInt(ord(v)) for v in self.value)
	
	def convert(self, other):
		if isinstance(other, BStr):
			return self
		elif isinstance(other, BList):
			return BList(BInt(ord(c)) for c in self.value)
		elif isinstance(other, BRegex):
			return BRegex(regex.compile(self.value,
				other.value.flags))
		elif isinstance(other, BFunc):
			tokens = BContext.tokenized(self.value)
			return BBlock(tokens)
		else:
			raise BCoercionError(self, other)

class BRegex(BChars):
	
	rank = 5
	
	regex_flag_chars = {
		'a': regex.ASCII,
		'b': regex.BESTMATCH,
		'f': regex.FULLCASE,
		'i': regex.IGNORECASE,
		'l': regex.LOCALE,
		'm': regex.MULTILINE,
		'e': regex.ENHANCEMATCH,
		'r': regex.REVERSE,
		's': regex.DOTALL,
		'u': regex.UNICODE,
		'v': regex.V1 if regex.DEFAULT_VERSION == regex.V0 else regex.V0,
		'w': regex.WORD,
		'x': regex.VERBOSE
	}
	
	default_flags = regex.DEFAULT_VERSION
	
	def __init__(self, value=None):
		value = value or ''
		if isinstance(value, type(regex.compile(''))):
			self.value = value
		else:
			self.value = regex.compile(str(value),
				BRegex.default_flags)
	
	def __repr__(self):
		escaped = escape_birdiescript(self.value.pattern)
		flags = ''.join(c for (c, f) in BRegex.regex_flag_chars.items()
			if f & self.value.flags)
		return safe_string('`' + escaped + '`' + flags)
	
	def __str__(self):
		return self.value.pattern
	
	def __eq__(self, other):
		if isinstance(other, BRegex):
			return ((self.value.pattern, self.value.flags) ==
				(other.value.pattern, other.value.flags))
		return super(BSeq, self).__eq__(other)
	
	def __lt__(self, other):
		if isinstance(other, BRegex):
			return ((self.value.pattern, self.value.flags) <
				(other.value.pattern, other.value.flags))
		return super(BSeq, self).__lt__(other)
	
	def __nonzero__(self):
		return bool(self.value.pattern)
	
	def format_value(self):
		return str(self)
	
	def simplify(self):
		return BList(BInt(ord(v)) for v in self.value.pattern)
	
	def convert(self, other):
		if isinstance(other, BRegex):
			return self
		elif isinstance(other, BList):
			return BList(map(ord, self.value.pattern))
		elif isinstance(other, BStr):
			return BStr(self.value.pattern)
		elif isinstance(other, BFunc):
			tokens = BContext.tokenized(self.value.pattern)
			return BBlock(tokens)
		else:
			raise BCoercionError(self, other)

class BFunc(BType):
	"""Base class for all Birdiescript function types."""

class BBlock(BFunc):
	
	rank = 6
	
	NONLOCAL = Sentinel('<nonlocal>')
	
	def __init__(self, value=None, scope=None, scoped=True):
		super(BFunc, self).__init__(value or [])
		self.scope = scope or {}
		self.scoped = scoped
	
	def __repr__(self):
		start = '{' if self.scoped else '\\{'
		return safe_string(start + ' '.join(map(str, self.value)) + '}')
	
	def __str__(self):
		start = '{' if self.scoped else '\\{'
		return start + ' '.join(map(str, self.value)) + '}'
	
	def __hash__(self):
		return hash(repr(self))
	
	def format_value(self):
		return str(self)
	
	def python_value(self):
		return self
	
	def tokenize(self):
		start = '{' if self.scoped else '\\{'
		tokens = [BToken('blockstart', start)]
		tokens += self.value
		tokens += [BToken('blockend', '}')]
		return tokens
	
	def convert(self, other):
		if isinstance(other, BList):
			return BList([BStr(str(v)) for v in self.value])
		elif isinstance(other, BChars):
			return type(other)(str(self))
		elif isinstance(other, BFunc):
			return self
		else:
			raise BCoercionError(self, other)
	
	def apply(self, context, looping=False):
		parent = context.subcontext(BBlock.NONLOCAL)
		parent.inherit_scope(self.scope)
		parent.looping = looping
		subcontext = context.subcontext(str(self))
		subcontext.parent = parent
		subcontext.tokens = copy.copy(self.value)
		subcontext.stack = context.stack
		subcontext.leftbs = context.leftbs
		if not self.scoped:
			subcontext.inherit_scope(self.scope)
		try:
			subcontext.execute()
		finally:
			parent.looping = False

class BBuiltin(BFunc):
	
	rank = 7
	
	def __init__(self, *names, **kwargs):
		if not names:
			raise TypeError('cannot instantiate unnamed builtin')
		super(BBuiltin, self).__init__(names)
		for name in names:
			if name in builtins:
				msg = 'cannot redefine builtin: {}'.format(
					repr(name))
				raise NameError(msg)
			builtins[name] = self
		value = kwargs.get('value', None)
		code = kwargs.get('code', None)
		doc = kwargs.get('doc', None)
		if value is not None:
			def builtin_apply(self, context):
				context.nesting += 1
				if context.debug:
					context.debug_print('[Value] {}'.format(
						repr(safe_string(value))),
						HEADER_COLORS)
					context.debug_print('Push value onto stack',
						colors.FG_YELLOW|colors.FG_NOBOLD)
				context.push(value)
				context.nesting -= 1
			if doc is not None:
				builtin_apply.__doc__ = doc
			self.__call__(builtin_apply)
		elif code is not None:
			def builtin_apply(self, context):
				context.nesting += 1
				if context.debug:
					context.debug_print('[Code] {}'.format(
						code), HEADER_COLORS)
				tokens = BContext.tokenized(code)
				if context.debug:
					context.debug_print('[Tokens] {}'.format(
						' '.join(map(str, tokens))),
						SUBHEADER_COLORS)
				context.print_state()
				context.execute_tokens(tokens)
				context.nesting -= 1
			if doc is not None:
				builtin_apply.__doc__ = doc
			self.__call__(builtin_apply)
	
	def __repr__(self):
		return safe_string('\\g' + self.value[0])
	
	def __str__(self):
		return self.value[0]
	
	def __hash__(self):
		return hash(repr(self))
	
	def __call__(self, f):
		"""
		Decorate a function with this builtin to use it as the apply() method.
		
		For example:
		
		@BBuiltin('+', 'Add'):
		def builtin_add(self, context):
			'''Addition.'''
			pass
		"""
		self.apply = types.MethodType(f, self)
		return f
	
	def format_value(self):
		return str(self)
	
	def python_value(self):
		return self
	
	def tokenize(self):
		return [BToken('prefixed', '\\:g' + self.value[0])]
	
	def simplify(self):
		return BBlock(self.tokenize())
	
	def coerce(self, other):
		return self.simplify()
	
	def convert(self, other):
		if isinstance(other, BList):
			return BStr(self.value).convert(BList())
		elif isinstance(other, BChars):
			return type(other)(str(self))
		elif isinstance(other, BFunc):
			return BBlock([BToken('name', str(self))])
		else:
			raise BCoercionError(self, other)
	
	def apply(self, context):
		msg = 'cannot call abstract builtin: {}'.format(repr(self.value))
		raise NotImplementedError(msg)


#################### Birdiescript parser ####################

def parse_int(token):
	bases = {'i':2, 't':3, 'q':4, 'p':5, 'h':6, 's':7, 'o':8, 'n':9,
		'k':10, 'u':11, 'z':12, 'r':13, 'w':14, 'v':15, 'x':16}
	if isinstance(token, BToken):
		token = token.text
	negative = False
	if token.endswith('m'):
		negative = True
		token = token[:-1]
	if any(token.endswith(b) for b in bases):
		token, base = token[:-1], bases[token[-1]]
		value = int(token, base)
	else:
		base = 16 if token.startswith('0') else 10
		value = int(token, base)
	if negative:
		value = -value
	return BInt(value)

def parse_complex(token):
	if isinstance(token, BToken):
		token = token.text
	if token.endswith('m'):
		token = '-' + token[:-1]
	token = token.replace('Inf', 'inf', 1).replace('Nan', 'nan', 1)
	if token.endswith('j'):
		return BComplex(complex(token))
	else:
		return BFloat(float(token))

def parse_chars(token):
	if isinstance(token, BToken):
		token = token.text
	if token == "'":
		token += "'"
	return BStr(token[1:])

def parse_herestr(token):
	if isinstance(token, BToken):
		token = token.text
	if token[-1] == '\n':
		token = token[:-1]
	return BStr(token[3:])

def parse_heredoc(token):
	if isinstance(token, BToken):
		token = token.text
	doc_name, token = regex.split(r'\s', token[2:], maxsplit=1)
	chomp = doc_name.startswith('-')
	if chomp:
		doc_name = doc_name[1:]
	token = regex.sub(regex.escape(doc_name) + '$', '', token, count=1)
	if chomp and token[-1] == '\n':
		token = token[:-1]
	return BStr(token)

string_char_rx = regex.compile(r'''
	(?P<backslash>\\\\)
	|(?P<backtick>\\`)
	|(?P<hexl>\\x[0-9a-f]{1,2})
	|(?P<hexu>\\X[0-9A-F]{1,2})
	|(?P<bmpl>\\u[0-9a-f]{1,4})
	|(?P<bmpu>\\U[0-9A-F]{1,4})
	|(?P<suppl>\\u[0-9a-f]{1,6})
	|(?P<suppu>\\U[0-9A-F]{1,6})
	|(?P<lit>.)
''', regex.VERSION1 | regex.DOTALL | regex.VERBOSE)

def string_char_parse_hex(x):
	i = int(x[2:], 16)
	if 0 <= i <= sys.maxunicode:
		return chr(i)
	return hex(i)[2:].lower()

string_char_parsers = {
	'backslash': lambda x: '\\',
	'backtick': lambda x: '`',
	'hexl': string_char_parse_hex,
	'hexu': string_char_parse_hex,
	'bmpl': string_char_parse_hex,
	'bmpu': string_char_parse_hex,
	'suppl': string_char_parse_hex,
	'suppu': string_char_parse_hex,
	'lit': identity
}

def sub_string_char_match(match):
	for (pattern, value) in match.groupdict().items():
		if value is None:
			continue
		char_parser = string_char_parsers.get(pattern, None)
		if char_parser:
			return char_parser(value)
	msg = 'error parsing string: {}'.format(repr(match.string))
	raise RuntimeError(msg)

def parse_string(token):
	if isinstance(token, BToken):
		token = token.text
	if not token.endswith('`'):
		token += '`'
	value = regex.sub(string_char_rx, sub_string_char_match, token[1:-1])
	return BStr(value)

regex_escape_rx = regex.compile(r'\\+`?', regex.VERSION1)

def sub_regex_escape_match(match):
	escape = match.string[match.start():match.end()]
	return escape[len(escape)//2:]

def parse_regex(token):
	if isinstance(token, BToken):
		token = token.text
	index = token.rindex('`')
	pattern, flags = token[1:index], token[index+1:]
	mask = 0
	for f in flags:
		mask |= BRegex.regex_flag_chars[f]
	if not mask:
		mask = BRegex.default_flags
	pattern = regex.sub(regex_escape_rx, sub_regex_escape_match, pattern)
	value = regex.compile(pattern, mask)
	return BRegex(value)

def parse_prefixed(token):
	if not isinstance(token, BToken):
		token = BToken('prefixed', token)
	elif token.text.startswith('\\}'):
		token.type = 'defcall'
		token.text = token.text[2:]
	elif token.text.startswith(':\\'):
		token.type = 'undef'
		token.text = token.text[2:]
	elif token.text.startswith('\\:'):
		token.type = 'call'
		token.text = token.text[2:]
	elif token.text.startswith(':'):
		token.type = 'def'
		token.text = token.text[1:]
	elif token.text.startswith('\\'):
		token.type = 'ref'
		token.text = token.text[1:]
	else:
		token.type = 'call'
		token.text = token.text[0].upper() + token.text[1:].lower()
		return token
	if token.text[0] in 'lgn':
		token.text = (token.text[0] + token.text[1].upper() +
			token.text[2:].lower())
	else:
		token.text = token.text[0].upper() + token.text[1:].lower()
	return token

class BToken(object):
	
	def __init__(self, type, text, pos=0):
		self.type = type
		self.text = text
		self.pos = pos
	
	def __repr__(self):
		return '{}({}, {}, {})'.format(self.__class__.__name__,
			repr(self.type), repr(self.text), repr(self.pos))
	
	def __str__(self):
		return self.text
	
	def __eq__(self, other):
		return self.type == other.type and self.text == other.text
	
	def parse(self):
		try:
			parser = BToken.parsers[self.type]
			return parser(self)
		except:
			msg = 'invalid token at character {}: {}'.format(
				self.pos, repr(self.text))
			raise SyntaxError(msg)
	
	parsers = {
		'comment': identity,
		'blockcomment': identity,
		'blockstart': identity,
		'blockend': identity,
		'prefixed': parse_prefixed,
		'ref': identity,
		'def': identity,
		'undef': identity,
		'call': identity,
		'int': parse_int,
		'complex': parse_complex,
		'str': parse_string,
		'chars': parse_chars,
		'herestr': parse_herestr,
		'heredoc': parse_heredoc,
		'regex': parse_regex,
		'name': parse_prefixed
	}


#################### Birdiescript interpreter ####################

# Built-in definitions
builtins = {}

class BContext(object):
	
	EXITED = Sentinel('<exited>')
	
	token_rx = regex.compile(r'''^\s*(?:
		(?P<comment> ::.*?(?:\n|$) )
		|(?P<herestr> \\\\\s.*?(?:\n|$) )
		|(?P<heredoc> \\\\-?(?P<heredelim>\S+)\s.*?(?:(?P=heredelim)|$) )
		|(?P<blockcomment> :\{{.*?(?::}}|$) )
		|(?P<blockstart> \\?\{{ )
		|(?P<blockend> }} )
		|(?:(?P<prefix> (?::\\|:|\\}}|\\:|\\) [lgn]? )?\s*(?:
			(?P<complex> (?:
				(?:[0-9]+\.[0-9]*|[0-9]*\.[0-9]+)
					(?:e-?[0-9]+)?
				|[1-9][0-9]*e-?[0-9]+
			)j?m?|[0-9]+jm? )
			|(?P<int> (?:
				[0-1]+i | [0-2]+t | [0-3]+q | [0-4]+p
				| [0-5]+h | [0-6]+s | [0-7]+o | [0-8]+n
				| [0-9]+k | [0-9][0-9a]*u | [0-9][0-9ab]*z
				| [0-9][0-9a-c]*r | [0-9][0-9a-d]*w
				| [0-9][0-9a-e]*v | [0-9][0-9a-f]*x
				| 0[0-9a-f]* | [0-9]+
			)m? )
			|(?P<regex> `(?:\\.|[^`])*`[abfilmersuvwx]+ )
			|(?P<str> `(?:\\.|[^`])*(?:`|$) )
			|(?P<chars> '(?:.[{Ll}]*|$) )
			|(?P<name> [^\s0-9:\\{{\}}`'][{Ll}]* )
			|(?P<invalid> \S+ )
		))
	)\s*'''.format(Ll=lower_rx),
		regex.VERSION1 | regex.DOTALL | regex.VERBOSE)
	
	@staticmethod
	def tokenized(script):
		context = BContext(script)
		context.tokenize()
		return context.tokens
	
	def __init__(self, script, encoding=None, debug=False, level=0):
		self.parent = None
		self.script = script
		self.tokens = None
		self.counter = 0
		self.stack = []
		self.scope = {}
		self.scoped = True
		self.encoding = encoding or sys.stdin.encoding or 'cp437'
		self.debug = debug
		self.level = level
		self.leftbs = []
		self.blocktokens = []
		self.blocklevel = 0
		self.scopedblock = True
		self.broken = False
		self.looping = False
		self.nesting = 0
		self.global_py_ns = {}
		self.local_py_ns = {}
	
	def tokenize(self):
		self.tokens = []
		n = len(self.script)
		at = 0
		while at < n:
			match = regex.match(BContext.token_rx,
				self.script[at:])
			if not match:
				msg = ('syntax error at character {}: {}'
					.format(at+1, repr(self.script[at])))
				raise SyntaxError(msg)
			prefix = match.groupdict().get('prefix', None)
			for (type, text) in match.groupdict().items():
				if text is None or type in ['prefix', 'invalid']:
					continue
				if prefix:
					token = BToken('prefixed',
						prefix+text, at+1)
				else:
					token = BToken(type, text, at+1)
				self.tokens.append(token)
				break
			else:
				token = self.script[at+match.start():
					at+match.end()]
				msg = ('invalid token at character {}: {}'
					.format(at+1, repr(str(token).rstrip())))
				raise SyntaxError(msg)
			at += match.end()
	
	def debug_print(self, value='', attrs=colors.DEFAULT_COLORS):
		if not self.debug:
			return
		indent = '    ' * (self.level + self.blocklevel + self.nesting)
		if not isinstance(value, str):
			value = str(value)
		lines = value.split('\n')
		msg = '\n'.join(indent + line.strip() for line in lines)
		colors.set_colors(attrs)
		print(safe_string(msg))
		colors.set_colors(colors.DEFAULT_COLORS)
	
	def print_state(self):
		if not self.debug:
			return
		stack = ' '.join(map(repr, self.stack))
		self.debug_print('[Stack] {}'.format(stack), STACK_COLORS)
		if self.scope:
			scope = ' '.join(n+':'+repr(v)
				for (n, v) in self.scope.items())
			self.debug_print('[Scope] {}'.format(scope),
				NOTE_COLORS)
		if self.leftbs:
			leftbs = ' '.join(map(str, self.leftbs))
			self.debug_print('[Lists] {}'.format(leftbs),
				NOTE_COLORS)
		if self.blocklevel:
			tokens = ' '.join(map(str, self.blocktokens))
			self.debug_print('[Block] {}'.format(tokens),
				NOTE_COLORS)
	
	def execute(self, printstack=False, repl=False):
		if self.tokens is None:
			self.tokenize()
		script = repr(self.script)
		if self.debug:
			self.debug_print('[Script] {}'.format(script),
				HEADER_COLORS)
		tokens = ' '.join(map(str, self.tokens))
		if self.debug:
			self.debug_print('[Tokens] {}'.format(tokens),
				SUBHEADER_COLORS)
			self.print_state()
		n = len(self.tokens)
		while self.counter < n and not self.broken:
			token = self.tokens[self.counter]
			self.execute_token(token)
			self.counter += 1
		if repl:
			return
		while self.blocklevel > 0 and not self.broken:
			token = BToken('blockend', '}', n)
			self.execute_token(token)
			n += 1
		if printstack and not self.broken:
			token = BToken('name', 'Pstack', n)
			self.execute_token(token)
	
	def execute_token(self, token):
		if self.broken:
			return
		if self.debug:
			self.debug_print('[Token] {}'.format(repr(token)),
				VALUE_COLORS)
		if token.type in ['comment', 'blockcomment']:
			if self.debug:
				self.debug_print('Comment')
			return
		elif token.type == 'blockstart':
			if self.blocklevel > 0:
				if self.debug:
					self.debug_print('Start block within block',
						INFO_COLORS)
				self.blocktokens.append(token)
			else:
				if self.debug:
					self.debug_print('Start block',
						INFO_COLORS)
				self.scopedblock = token.text != '\\{'
			self.blocklevel += 1
			self.print_state()
			return
		elif token.type == 'blockend':
			if self.blocklevel > 1:
				if self.debug:
					self.debug_print('End block within block',
						INFO_COLORS)
				self.blocktokens.append(token)
				self.blocklevel -= 1
				self.print_state()
				return
			if self.debug:
				self.debug_print('End block',
					INFO_COLORS)
			self.blocklevel -= 1
			if self.blocklevel < 0:
				self.blocklevel = 0
				if self.debug:
					self.debug_print("Warning: '}' without '{'; "
						"pushing empty block", ALERT_COLORS)
			value = BBlock(self.blocktokens, self.scope, self.scopedblock)
			self.blocktokens = []
			self.scopedblock = True
		elif token.type == 'defcall' or (token.type == 'prefixed' and
			token.text.startswith('\\}')):
			if token.type == 'prefixed':
				token = parse_prefixed(token)
			if self.blocklevel > 1:
				if self.debug:
					self.debug_print('End block within block; '
						'define and call as: {}'
						.format(token.text), INFO_COLORS)
				self.blocktokens.append(token)
				self.blocklevel -= 1
				self.print_state()
				return
			if self.debug:
				self.debug_print('End block; define and call as: {}'
					.format(token.text), INFO_COLORS)
			self.blocklevel -= 1
			if self.blocklevel < 0:
				self.blocklevel = 0
				if self.debug:
					self.debug_print("Warning: '\\}' without '{'; "
						"pushing empty block", ALERT_COLORS)
			value = BBlock(self.blocktokens, self.scope, self.scopedblock)
			self.blocktokens = []
			self.scopedblock = True
			self.define(token.text, value)
			if self.debug:
				self.debug_print('[Deref] {}'.format(
					repr(safe_string(value))), VALUE_COLORS)
			value.apply(self)
			self.print_state()
			return
		else:
			if self.blocklevel > 0:
				if self.debug:
					self.debug_print('Add token to block',
						INFO_COLORS)
				self.blocktokens.append(token)
				self.print_state()
				return
			value = token.parse()
		if self.debug:
			self.debug_print('[Value] {}'.format(
				repr(safe_string(value))), VALUE_COLORS)
		if isinstance(value, BType):
			try:
				deref = self.dereference(token.text)
				if self.debug:
					self.debug_print('Call dereferenced value',
						INFO_COLORS)
					self.debug_print('[Deref] {}'.format(
						repr(safe_string(deref))),
						VALUE_COLORS)
				deref.apply(self)
			except NameError:
				if self.debug:
					self.debug_print('Push value onto stack',
						INFO_COLORS)
				self.push(value)
		elif value.type == 'ref':
			if self.debug:
				self.debug_print('Push dereferenced value onto stack',
					INFO_COLORS)
			deref = self.dereference(value.text)
			if self.debug:
				self.debug_print('[Deref] {}'.format(
					repr(safe_string(deref))), VALUE_COLORS)
			self.push(deref)
		elif value.type == 'def':
			if self.debug:
				self.debug_print('Define value at top of stack as: {}'
					.format(value.text), INFO_COLORS)
			self.define(value.text, self.top())
		elif value.type == 'undef':
			if self.debug:
				self.debug_print('Undefine: {}'.format(value.text),
					INFO_COLORS)
			self.undefine(value.text)
		elif value.type == 'call':
			if self.debug:
				self.debug_print('Call dereferenced value',
					INFO_COLORS)
			deref = self.dereference(value.text)
			if self.debug:
				self.debug_print('[Deref] {}'.format(
					repr(safe_string(deref))), VALUE_COLORS)
			deref.apply(self)
		self.print_state()
	
	def execute_tokens(self, tokens):
		for token in tokens:
			self.execute_token(token)
			if self.broken:
				break
	
	def define(self, ref, value, nonloc=True):
		if ref.startswith('g'):
			# Global (outermost) scope
			aref = ref[1:]
			if not self.parent:
				self.scope[aref] = value
			else:
				self.parent.define(ref, value)
		elif ref.startswith('n'):
			# Innermost nonlocal scope
			aref = ref[1:]
			if (not nonloc and aref in self.scope) or not self.parent:
				self.scope[aref] = value
			else:
				self.parent.define(ref, value, False)
		else:
			# Local scope
			if ref.startswith('l'):
				ref = ref[1:]
			self.scope[ref] = value
	
	def undefine(self, ref, nonloc=True):
		if ref.startswith('g'):
			# Global (outermost) scope
			aref = ref[1:]
			if not self.parent:
				if aref in self.scope:
					del self.scope[aref]
			else:
				self.parent.undefine(ref)
		elif ref.startswith('n'):
			# Innermost nonlocal scope
			aref = ref[1:]
			if (not nonloc and aref in self.scope) or not self.parent:
				if aref in self.scope:
					del self.scope[aref]
			else:
				self.parent.undefine(ref, False)
		else:
			# Local scope
			if ref.startswith('l'):
				ref = ref[1:]
			if ref in self.scope:
				del self.scope[ref]
	
	def dereference(self, ref):
		if ref.startswith('g'):
			# Global (outermost) scope
			if self.parent:
				try:
					return self.parent.dereference(ref)
				except NameError:
					pass
			aref = ref[1:]
			if aref in builtins:
				return builtins[aref]
			elif aref in self.scope:
				return self.scope[aref]
			raise NameError('undefined name: {}'.format(repr(aref)))
		if ref.startswith('n'):
			ref = ref[1:]
		else:
			if ref.startswith('l'):
				ref = ref[1:]
			if ref in self.scope:
				return self.scope[ref]
		if self.parent:
			return self.parent.dereference(ref)
		if ref in builtins:
			return builtins[ref]
		raise NameError('undefined name: {}'.format(repr(ref)))
	
	def adjust_leftbs(self, old_n):
		d = old_n - len(self.stack)
		if d <= 0:
			return
		for (i, c) in reversed(list(enumerate(self.leftbs))):
			if c < old_n:
				break
			self.leftbs[i] -= d
	
	def push(self, x):
		self.stack.append(x)
	
	def queue(self, x):
		self.stack.insert(0, x)
	
	def pop(self, i=-1):
		n = len(self.stack)
		if not n:
			self.debug_print('Warning: pop from empty stack; '
				'popping 0', ALERT_COLORS)
			return BInt(0)
		x = self.stack.pop(i)
		self.adjust_leftbs(len(self.stack) + 1)
		return x
	
	def dequeue(self):
		return self.pop(0)
	
	def pop_n(self, n=1):
		x = []
		for i in range(n):
			x.insert(0, self.pop())
		return x
	
	def pop_till(self, n):
		if n < 0:
			n += len(self.stack)
		return self.pop_n(len(self.stack)-n)
	
	def peek(self, k=-1):
		if k in [0, -1] and not self.stack:
			self.debug_print('Warning: peek at empty stack; '
				'returning 0', ALERT_COLORS)
			self.push(BInt(0))
		return self.stack[k]
	
	def top(self):
		return self.peek(-1)
	
	def replace_stack(self, stack):
		n = len(self.stack)
		self.stack = stack
		self.adjust_leftbs(n)
	
	def subcontext(self, script):
		context = BContext(script, encoding=self.encoding,
			debug=self.debug, level=self.level+1)
		context.parent = self
		context.global_py_ns = self.global_py_ns
		context.nesting = self.nesting
		return context
	
	def inherit_scope(self, scope):
		self.scoped = False
		self.scope = scope


#################### Command-line interface ####################

def predefine_variables(context, filename, script, argv):
	context.scope['A'] = BList(map(BStr, argv))
	context.scope['_f'] = BStr(filename)
	context.scope['_s'] = BStr(script)
	context.scope['_d'] = BStr(time.strftime('%b %d %Y'))
	context.scope['_t'] = BStr(time.strftime('%H:%M:%S'))
	context.scope['_v'] = BStr(version)

def execute_file(filename, script, argv, encoding, debug):
	context = BContext(script, encoding, debug)
	predefine_variables(context, filename, script, argv)
	try:
		context.execute(printstack=True)
	except Exception as ex:
		sys.stdout.flush()
		colors.set_colors(ALERT_COLORS)
		print('Error: {}'.format(ex))
		if debug:
			traceback.print_exc(ex)
		colors.set_colors(colors.DEFAULT_COLORS)
		sys.exit(1)

def repl_environment(argv, encoding, debug):
	context = BContext('', encoding, False)
	predefine_variables(context, '', '', argv)
	context.tokenize()
	colors.set_colors(colors.FG_GREY|colors.FG_BOLD)
	print('Birdiescript {} ({}, {}) [Python {}]'.format(
		context.scope['_v'], context.scope['_d'], context.scope['_t'],
		platform.python_version()))
	colors.set_colors(colors.DEFAULT_COLORS)
	while not context.broken:
		print()
		stack = ' '.join(map(repr, context.stack))
		colors.set_colors(STACK_COLORS)
		print('[Stack] {}'.format(stack))
		if context.blocklevel:
			level = context.blocklevel
			tokens = ' '.join(map(str, context.blocktokens))
			colors.set_colors(colors.FG_YELLOW|colors.FG_NOBOLD)
			print('[Block] {}'.format(tokens))
		colors.set_colors(VALUE_COLORS)
		if readline:
			script = input('>>> ')
			colors.set_colors(colors.DEFAULT_COLORS)
		else:
			print('>>> ', end='')
			colors.set_colors(colors.DEFAULT_COLORS)
			script = input()
		try:
			tokens = BContext.tokenized(script)
			context.script += script
			context.tokens.extend(tokens)
			try:
				context.execute(repl=True)
			except Exception as ex:
				context.tokens = context.tokens[:context.counter]
				raise
		except Exception as ex:
			colors.set_colors(ALERT_COLORS)
			print('Error: {}'.format(ex))
			if debug:
				traceback.print_exc()
			colors.set_colors(colors.DEFAULT_COLORS)

class BirdiescriptHelpFormatter(argparse.RawDescriptionHelpFormatter):
	
	def __init__(self, prog, indent_increment=2, max_help_position=24,
		width=None):
		super(BirdiescriptHelpFormatter, self).__init__(prog,
			indent_increment, max_help_position, width)
		if self._width > 70:
			self._width = 70

def main():
	if not using_regex_module:
		colors.set_colors(colors.FG_RED|colors.FG_NOBOLD)
		print("Warning: 'regex' module not available, default to 're'")
		print("Install 'regex' from <https://pypi.python.org/pypi/regex>")
		colors.set_colors(colors.DEFAULT_COLORS)
		print()
	
	encoding = sys.stdin.encoding or 'cp437'
	
	parser = argparse.ArgumentParser(description='Birdiescript interpreter.',
		epilog='With no FILE, or when FILE is -, read standard input. Set the\n'
			'PYTHONIOENCODING environment variable to specify the standard\n'
			'input character encoding.\n\n'
			'Copyright (C) 2013-2014 Remy Oukaour <http://www.remyoukaour.com>.\n'
			'MIT License.\n'
			'This is free software: you are free to change and redistribute it.\n'
			'There is NO WARRANTY, to the extent permitted by law.\n',
		formatter_class=BirdiescriptHelpFormatter,
		add_help=False)
	parser.add_argument('FILE', nargs='?',
		help='run contents of FILE as a script')
	parser.add_argument('ARGS', nargs='...',
		help='arguments to script')
	parser.add_argument('-c', '--cmd', metavar='CMD',
		help='run CMD string as a script')
	parser.add_argument('-d', '--debug', action='store_const', const=True,
		help='show debug output when running script')
	parser.add_argument('-e', '--encoding', metavar='ENC',
		default=encoding,
		help='specify the script character encoding [default: ' +
			encoding + ']')
	parser.add_argument('-h', '--help', action='help',
		help='show this help message and exit')
	parser.add_argument('-m', '--maxdepth', metavar='DEPTH',
		help='set maximum recursion depth')
	parser.add_argument('-r', '--repl', action='store_const', const=True,
		help='run as REPL environment')
	parser.add_argument('-v', '--version', action='version',
		version='%(prog)s {}'.format(version))
	
	args = vars(parser.parse_args(sys.argv[1:]))
	
	default_limit = sys.getrecursionlimit()
	try:
		limit = int(args.get('maxdepth', 0))
		sys.setrecursionlimit(limit)
	except:
		sys.setrecursionlimit(default_limit)
	
	argv = args.get('ARGS', [])
	debug = args.get('debug', False)
	encoding = args.get('encoding')
	
	if args.get('cmd', None) is not None:
		# Execute script from -c/--cmd flag
		filename = ''
		script = args['cmd']
		arg1 = args.get('FILE', None)
		if arg1 is not None:
			argv.insert(0, arg1)
		execute_file(filename, script, argv, encoding, debug)
	elif args.get('repl', False):
		# Run an interactive REPL environment
		arg1 = args.get('FILE', None)
		if arg1 is not None:
			argv.insert(0, arg1)
		repl_environment(argv, encoding, debug)
	elif args.get('FILE', None) not in [None, '-']:
		# Execute script read from FILE
		filename = args['FILE']
		try:
			with codecs.open(filename, 'rU', encoding) as file:
				script = file.read()
		except Exception as ex:
			print(ex)
			exit(1)
		execute_file(filename, script, argv, encoding, debug)
	elif not sys.stdin.isatty():
		# Execute script read from stdin
		filename = '<stdin>'
		try:
			script = sys.stdin.read()
		except Exception as ex:
			print(ex)
			exit(1)
		execute_file(filename, script, argv, encoding, debug)
	else:
		# Run an interactive REPL environment
		repl_environment(argv, encoding, debug)
