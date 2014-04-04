# -*- coding: utf-8 -*-
"""
Birdiescript built-in definitions.
"""


#################### Imports ####################

from __future__ import (absolute_import, division, generators, nested_scopes,
	print_function, unicode_literals, with_statement)

from .core import *


#################### Utility functions ####################

def merge_flags(af, bf):
	"""Return merged regex flags."""
	flags = af | bf
	if flags & (regex.VERSION0 | regex.VERSION1):
		flags &= ~regex.DEFAULT_VERSION
	if flags & (regex.ASCII | regex.LOCALE | regex.UNICODE):
		flags &= ~(regex.ASCII | regex.LOCALE)
	return flags

def areinstances(objects, classes):
	"""Return whether all of the objects are instances of the classes."""
	return all(isinstance(obj, classes) for obj in objects)

def signature(*types):
	"""
	Return a decorator which allows a function to be decorated with a builtin.
	
	For example:
	
	# ( a b -- a//b a%b )
	@BBuiltin('Divmod')
	@signature(BInt, BInt)
	def builtin_divmod(a, b):
		'''Division and modulus.'''
		d = BInt(a.value // b.value)
		m = BInt(a.value % b.value)
		return (d, m)
	"""
	arity = len(types)
	def decorator(func):
		@functools.wraps(func)
		def builtin_apply(self, context, looping=False):
			def apply_with(args):
				results = func(*args)
				if isinstance(results, BType):
					results = (results,)
				if results is None:
					return
				for result in results:
					context.push(result)
			args = [context.pop() for i in range(arity)][::-1]
			for (i, arg) in enumerate(args):
				if not isinstance(arg, types[i]):
					break
			else:
				apply_with(args)
				return
			if len(types) == 2 and types[0] != types[1]:
				rargs = args[::-1]
				for (i, arg) in enumerate(rargs):
					if not isinstance(arg, types[i]):
						break
				else:
					apply_with(rargs)
					return
			raise BTypeError(self, args)
		return builtin_apply
	return decorator

# Shorthand for generic types when calling signature()
_ = BType

def complex_gamma(z):
	"""Return the gamma function of z."""
	# Taken from LiteratePrograms
	# <http://en.literateprograms.org/Gamma_function_with_the_Lanczos_approximation_%28Python%29>
	g = 7
	lanczos = [0.99999999999980993, 676.5203681218851,
		-1259.1392167224028, 771.32342877765313,
		-176.61502916214059, 12.507343278686905,
		-0.13857109526572012, 9.9843695780195716e-6,
		1.5056327351493116e-7]
	if z.real < 0.5:
		return math.pi / (cmath.sin(math.pi*z) * complex_gamma(1-z))
	z -= 1
	x = lanczos[0]
	for i in range(1, g+2):
		x += lanczos[i] / (z+i)
	t = z + g + 0.5
	return math.sqrt(2*math.pi) * t**(z+0.5) * cmath.exp(-t) * x


#################### Stack operations ####################

@BBuiltin('#t', 'Depth')
def builtin_depth(self, context, looping=False):
	"""Number of items of the stack."""
	context.push(BInt(len(context.stack)))

@BBuiltin(';s', 'Clr', 'Clear')
def builtin_clear(self, context, looping=False):
	"""Modify the stack: ( ... -- )."""
	while context.stack:
		context.pop()

@BBuiltin(';', 'Pop')
@signature(_)
def builtin_pop(a):
	"""Modify the stack: ( a -- )."""
	pass

@BBuiltin(',', 'Dup', '′', code='0,k')
@signature(_)
def builtin_dup(a):
	"""Modify the stack: ( a -- a a )."""
	a2 = type(a)(a.value)
	return (a, a2)

BBuiltin('″', code=',,', doc="""Modify the stack: ( a -- a a a ).""")
BBuiltin('‴', code=',,,', doc="""Modify the stack: ( a -- a a a a ).""")

BBuiltin(',q', 'Qdup', code=',\\,It',
	doc="""Duplicate the top of the stack if it is true.""")

@BBuiltin('?', 'Over', code='1,k')
@signature(_, _)
def builtin_over(a, b):
	"""Modify the stack: ( a b -- a b a )."""
	a2 = type(a)(a.value)
	return (a, b, a2)

@BBuiltin('$', 'Swap', code='1@k')
@signature(_, _)
def builtin_swap(a, b):
	"""Modify the stack: ( a b -- b a )."""
	return (b, a)

@BBuiltin('@', 'Rot', code='2@k')
@signature(_, _, _)
def builtin_rotate(a, b, c):
	"""Modify the stack: ( a b c -- b c a )."""
	return (b, c, a)

BBuiltin('@n', '-rot', 'Θ', code='@@',
	doc="""Modify the stack: ( a b c -- c a b ).""")

@BBuiltin(';p', 'Nip', '£', code='$;')
@signature(_, _)
def builtin_nip(a, b):
	"""Modify the stack: ( a b -- b )."""
	return b

@BBuiltin('?p', 'Tuck', '¿', code='$?')
@signature(_, _)
def builtin_tuck(a, b):
	"""Modify the stack: ( a b -- b a b )."""
	b2 = type(b)(b.value)
	return (b2, a, b)

BBuiltin(',p', 'Dupbelow', code='?$', altcode='$,@',
	doc="""Modify the stack: ( a b -- a a b ).""")

BBuiltin('$p', 'Swapbelow', code='@$',
	doc="""Modify the stack: ( a b c -- b a c ).""")

BBuiltin(';t', 'Poptwo', code=';;',
	doc="""Modify the stack: ( a b -- ).""")

@BBuiltin(',t', 'Duptwo', '⁇', code='??')
@signature(_, _)
def builtin_2dup(a, b):
	"""Modify the stack: ( a b -- a b a b )."""
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, a2, b2)

@BBuiltin('?t', 'Overtwo', code='3?k3?k')
@signature(_, _, _, _)
def builtin_2over(a, b, c, d):
	"""Modify the stack: ( a b c d -- a b c d a b )."""
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, c, d, a2, b2)

@BBuiltin('$t', 'Swaptwo', code='3@k3@k')
@signature(_, _, _, _)
def builtin_2swap(a, b, c, d):
	"""Modify the stack: ( a b c d -- c d a b )."""
	return (c, d, a, b)

@BBuiltin('@t', 'Rottwo', code='5@k5@k')
@signature(_, _, _, _, _, _)
def builtin_2rotate(a, b, c, d, e, f):
	"""Modify the stack: ( a b c d e f -- c d e f a b )."""
	return (c, d, e, f, a, b)

@BBuiltin('©t', '-rottwo', code='@t@t')
@signature(_, _, _, _, _, _)
def builtin_2nrotate(a, b, c, d, e, f):
	"""Modify the stack: ( a b c d e f - e f a b c d )."""
	return (e, f, a, b, c, d)

@BBuiltin(';pt', 'Niptwo', '£t', code='$t;t')
@signature(_, _, _, _)
def builtin_2nip(a, b, c, d):
	"""Modify the stack: ( a b c d -- c d )."""
	return (c, d)

@BBuiltin('?pt', 'Tucktwo', '¿t', code='$t?t')
@signature(_, _, _, _)
def builtin_2tuck(a, b, c, d):
	"""Modify the stack: ( a b c d -- c d a b c d )."""
	c2 = type(c)(c.value)
	d2 = type(d)(d.value)
	return (c2, d2, a, b, c, d)

BBuiltin(',pt', 'Dupbelowtwo', code='?t$t',
	doc="""Modify the stack: ( a b c d -- a b a b c d ).""")

BBuiltin('$pt', 'Swapbelowtwo', code='@t$t',
	doc="""Modify the stack: ( a b c d e f - c d a b e f ).""")

BBuiltin(';r', 'Popthree', code=';;;',
	doc="""Modify the stack: ( a b c -- ).""")

@BBuiltin(',r', 'Dupthree')
@signature(_, _, _)
def builtin_3dup(a, b, c):
	"""Modify the stack: ( a b c -- a b c a b c )."""
	c2 = type(c)(c.value)
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, c, a2, b2, c2)

BBuiltin(';f', 'Popfour', code=';;;;',
	doc="""Modify the stack: ( a b c d -- ).""")

@BBuiltin(',f', 'Dupfour')
@signature(_, _, _, _)
def builtin_4dup(a, b, c, d):
	"""Modify the stack: ( a b c d -- a b c d a b c d )."""
	d2 = type(d)(d.value)
	c2 = type(c)(c.value)
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, c, d, a2, b2, c2, d2)

BBuiltin(';v', 'Popfive', code=';;;;;',
	doc="""Modify the stack: ( a b c d e -- ).""")

@BBuiltin(',v', 'Dupfive')
@signature(_, _, _, _, _)
def builtin_5dup(a, b, c, d, e):
	"""Modify the stack: ( a b c d e -- a b c d e a b c d e )."""
	e2 = type(e)(e.value)
	d2 = type(d)(d.value)
	c2 = type(c)(c.value)
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, c, d, e, a2, b2, c2, d2, e2)

BBuiltin(';x', 'Popsix', code=';;;;;;',
	doc="""Modify the stack: ( a b c d e f -- ).""")

@BBuiltin(',x', 'Dupsix')
@signature(_, _, _, _, _, _)
def builtin_6dup(a, b, c, d, e, f):
	"""Modify the stack: ( a b c d e f -- a b c d e f a b c d e f )."""
	f2 = type(f)(f.value)
	e2 = type(e)(e.value)
	d2 = type(d)(d.value)
	c2 = type(c)(c.value)
	b2 = type(b)(b.value)
	a2 = type(a)(a.value)
	return (a, b, c, d, e, f, a2, b2, c2, d2, e2, f2)

@BBuiltin(',k', 'Pick')
def builtin_pick(self, context, looping=False):
	"""Copy the item at a given index to the top of the stack."""
	k = context.pop()
	if isinstance(k, BNum):
		ks = [~int(k.simplify().value)]
	elif isinstance(k, BSeq):
		ks = [~int(v.simplify().value) for v in k.simplify().value]
	else:
		raise BTypeError(self, k)
	n = len(context.stack)
	ks = [kv+n if kv < 0 else kv for kv in ks]
	aks = [context.peek(kv) for kv in ks]
	for ak in aks:
		context.push(ak)

@BBuiltin('@k', 'Roll')
def builtin_roll(self, context, looping=False):
	"""Move the item at a given index to the top of the stack."""
	k = context.pop()
	if isinstance(k, BNum):
		ks = [~int(k.simplify().value)]
	elif isinstance(k, BSeq):
		ks = [~int(v.simplify().value) for v in k.simplify().value]
	else:
		raise BTypeError(self, k)
	n = len(context.stack)
	ks = [kv+n if kv < 0 else kv for kv in ks]
	aks = [context.peek(kv) for kv in ks]
	# Adjust list mark
	ks = set(ks)
	queue = []
	for kv in ks:
		queue.append(context.pop())
	while queue:
		context.push(queue.pop())
	# Remove rolled items
	for i in sorted(ks, reverse=True):
		del context.stack[i]
	for ak in aks:
		context.push(ak)

@BBuiltin('(s', 'Shelve', code='#t({1_@k}*')
def builtin_shelve(self, context, looping=False):
	"""Modify the stack: ( ... a -- a ... )."""
	a = context.pop()
	context.queue(a)

@BBuiltin(')s', 'Unshelve', code='1_@k')
def builtin_unshelve(self, context, looping=False):
	"""Modify the stack: ( a ... -- ... a )."""
	a = context.dequeue()
	context.push(a)


#################### Overloaded (polymorphic) operators ####################

@BBuiltin('+', 'Add', 'Concat', 'Concatenate', 'Append', 'Prepend', 'Extend',
	'Compose', 'Curry')
def builtin_add_overloaded(self, context, looping=False):
	"""
	Add two numbers.
	Concatenate two sequences.
	Append/prepend a number to a sequence, depending on their order.
	Compose two functions.
	Curry a function with a number or sequence.
	"""
	b = context.pop()
	a = context.pop()
	aa, bb = BType.commonize(a, b)
	if areinstances((aa, bb), BNum):
		# Add two numbers
		try:
			c = type(aa)(aa.value + bb.value)
		except:
			c = BFloat(float('nan'))
		context.push(c)
	elif areinstances((aa, bb), BRegex):
		# Concatenate two regexes
		pattern = aa.value.pattern + bb.value.pattern
		flags = merge_flags(aa.value.flags, bb.value.flags)
		c = BRegex(regex.compile(pattern, flags))
		context.push(c)
	elif areinstances((aa, bb), BSeq):
		# Concatenate two sequences
		c = type(aa)(aa.value + bb.value)
		context.push(c)
	elif areinstances((aa, bb), BFunc):
		# Compose two functions
		c = BBlock(aa.value + bb.value)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('-', 'Sub', 'Subtract', 'Each', '∖')
def builtin_subtract_overloaded(self, context, looping=False):
	"""
	Subtract two numbers.
	Asymmetric difference of two sequences.
	Execute a function with each item in a sequence.
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	aa, bb = BType.commonize(a, b)
	if areinstances((aa, bb), BNum):
		# Subtract two numbers
		c = type(aa)(aa.value - bb.value)
		context.push(c)
	elif areinstances((aa, bb), BSeq):
		# Asymmetric difference for two sequences
		av = aa.simplify().value
		bv = bb.simplify().value
		cv = BList([v for v in av if v not in bv]).convert(aa).value
		c = type(aa)(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Execute function with each item in sequence
		for x in b.simplify().value:
			context.push(x)
			a.apply(context)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('*', 'Mul', 'Mult', 'Multiply', 'Rep', 'Repeat', 'Replicate', 'Join',
	'Times', 'Fold', 'Reduce', 'Inject')
def builtin_multiply_overloaded(self, context, looping=False):
	"""
	Multiply two numbers.
	Repeat a sequence a number of times.
	Join the items of a sequence with another sequence.
	Execute a function a number of times.
	Fold a sequence with a binary function.
	Combine two unary functions into one with the effect: ( a b -- F(a) G(b) ).
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BNum):
		# Multiply two numbers
		aa, bb = BType.commonize(a, b)
		c = type(aa)(aa.value * bb.value)
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, BNum):
		# Repeat sequence a number of times
		n = int(b.simplify().value)
		if isinstance(a, BRegex):
			cv = regex.compile(a.value.pattern*n, a.value.flags)
		else:
			cv = a.value * n
		c = type(a)(cv)
		context.push(c)
	elif areinstances((a, b), BSeq):
		# Join sequence with sequence
		if isinstance(a, BList):
			if isinstance(b, BList):
				# Join list with list
				av = a.value[:]
				cv = []
				while av:
					cv.append(av.pop(0))
					if av:
						cv.extend(b.value)
				context.push(BList(cv))
			elif isinstance(b, BStr):
				# Join list with string
				av = [x.convert(BStr()).value
					for x in a.value]
				cv = b.value.join(av)
				context.push(BStr(cv))
			elif isinstance(b, BRegex):
				# Join list with regex
				av = [x.convert(BStr()).value
					for x in a.value]
				pattern = b.value.pattern.join(av)
				cv = regex.compile(pattern, b.value.flags)
				context.push(BRegex(cv))
		elif isinstance(a, BStr):
			if isinstance(b, BList):
				# Join string with list
				bv = b.convert(BStr()).value
				cv = bv.join(a.value)
				context.push(BStr(cv))
			elif isinstance(b, BStr):
				# Join string with string
				cv = b.value.join(a.value)
				context.push(BStr(cv))
			elif isinstance(b, BRegex):
				# Join string with regex
				pattern = b.value.pattern.join(a.value)
				cv = regex.compile(pattern, b.value.flags)
				context.push(BRegex(cv))
		elif isinstance(a, BRegex):
			if isinstance(b, BList):
				# Join regex with list
				bv = b.convert(BStr()).value
				pattern = bv.join(a.value.pattern)
				cv = regex.compile(pattern, a.value.flags)
				context.push(BStr(cv))
			elif isinstance(b, BStr):
				# Join regex with string
				pattern = b.value.join(a.value.pattern)
				cv = regex.compile(pattern, a.value.flags)
				context.push(BRegex(cv))
			elif isinstance(b, BRegex):
				# Join regex with regex
				pattern = b.value.pattern.join(a.value.pattern)
				flags = merge_flags(a.value.flags, b.value.flags)
				cv = regex.compile(pattern, flags)
				context.push(BRegex(cv))
	elif isinstance(a, BFunc) and isinstance(b, BNum):
		# Execute function a number of times
		n = int(b.simplify().value)
		for i in range(n):
			a.apply(context)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Fold sequence with function
		bv = b.simplify().value[:]
		context.push(bv.pop(0))
		while bv:
			context.push(bv.pop(0))
			a.apply(context)
	elif areinstances((a, b), BFunc):
		# Combine two unary functions: ( a b -- F(a) G(b) )
		c = BBlock()
		c.value.append(BToken('name', '$'))
		c.value.extend(a.convert(BBlock()).value)
		c.value.append(BToken('name', '$'))
		c.value.extend(b.convert(BBlock()).value)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('/', '÷', 'Div', 'Divide', 'Chunk', 'Split', 'Part', 'Partition',
	'Unfold', '⁄')
def builtin_divide_overloaded(self, context, looping=False):
	"""
	Divide two numbers.
	Chunk a sequence by a number.
	Split a sequence around another sequence.
	Partition a sequence with a predicate function.
	Unfold a seed value with a predicate function and an unspool function.
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BNum):
		# Divide two numbers
		aa, bb = BType.commonize(a, b)
		try:
			cv = aa.value / bb.value
		except:
			cv = float('nan')
		c = BType.from_python(cv).simplify()
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, BNum):
		# Chunk sequence by number
		n = int(b.simplify().value)
		mod = reversed if n < 0 else identity
		n = abs(n)
		if not n:
			raise ZeroDivisionError('cannot chunk by zero')
		cv = []
		if isinstance(a, BRegex):
			av = a.value.pattern
			while av:
				xv, av = av[:n], av[n:]
				x = BRegex(xv, a.value.flags)
				cv.append(x)
		else:
			av = a.value
			while av:
				xv, av = av[:n], av[n:]
				x = type(a)(xv)
				cv.append(x)
		c = BList(mod(cv))
		context.push(c)
	elif areinstances((a, b), BSeq):
		# Split sequence around sequence
		aa, bb = BType.commonize(a, b)
		av, bv = aa.simplify().value[:], bb.simplify().value
		if not av:
			cv = []
		elif not bv:
			cv = [BList([x]).convert(aa) for x in av]
		else:
			n = len(bv)
			cv, xv = [], []
			while av:
				while av and av[:n] != bv:
					xv.append(av.pop(0))
				cv.append(BList(xv).convert(aa))
				if av == bv:
					cv.append(BList().convert(aa))
				av = av[n:]
				xv = []
		c = BList(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Partition sequence with predicate function
		tv, fv = [], []
		bv = b.simplify().value
		for x in bv:
			context.push(x)
			a.apply(context)
			if context.pop():
				tv.append(x)
			else:
				fv.append(x)
		t = BList(tv).convert(b)
		f = BList(fv).convert(b)
		c = BList([t, f])
		context.push(c)
	elif areinstances((a, b), BFunc):
		# Unfold with predicate and unspool functions
		cv = []
		while not context.broken:
			x = context.top()
			x2 = type(x)(x.value)
			context.push(x2)
			a.apply(context)
			if not context.pop():
				break
			cv.append(context.top())
			b.apply(context, looping=True)
		if context.broken != BContext.EXITED:
			context.broken = False
		context.pop()
		context.push(BList(cv))
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('%', 'Mod', 'Modulo', 'Step', 'Skip', 'Splitf', 'Scan')
def builtin_modulo_overloaded(self, context, looping=False):
	"""
	Modulo two numbers.
	Step through a sequence by a number.
	Split a sequence around another sequence, removing empty subsequences.
	Scan a sequence with a binary function.
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BNum):
		# Modulo two numbers
		aa, bb = BType.commonize(a, b)
		try:
			if areinstances((aa, bb), BFloat):
				cv = math.fmod(aa.value, bb.value)
			else:
				cv = aa.value % bb.value
		except:
			cv = float('nan')
		c = BType.from_python(cv)
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, BNum):
		# Step through sequence by number
		i = int(b.simplify().value)
		if isinstance(a, BRegex):
			pv = a.value.pattern[::i]
			try:
				cv = regex.compile(pv, a.value.flags)
				c = BRegex(cv)
			except:
				c = BStr(pv)
		else:
			cv = a.value[::i]
			c = type(a)(cv)
		context.push(c)
	elif areinstances((a, b), BSeq):
		# Split sequence around sequence, removing empty subsequences
		aa, bb = BType.commonize(a, b)
		av, bv = aa.simplify().value[:], bb.simplify().value
		if not av:
			cv = []
		elif not bv:
			cv = [BList([x]).convert(aa) for x in av]
		else:
			n = len(bv)
			cv, xv = [], []
			while av:
				while av and av[:n] != bv:
					xv.append(av.pop(0))
				if xv:
					cv.append(BList(xv).convert(aa))
				av = av[n:]
				xv = []
		c = BList(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Scan sequence with function
		bv = b.simplify().value[:]
		cv = []
		context.push(bv.pop(0))
		cv.append(context.top())
		while bv:
			context.push(bv.pop(0))
			a.apply(context)
			cv.append(context.top())
		context.pop()
		c = BList(cv)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('&', 'Intersect', 'Filter', 'Select', '∩')
def builtin_bitwise_and_overloaded(self, context, looping=False):
	"""
	Bitwise 'and' of two integers.
	Intersection of two sequences.
	Filter a sequence by a predicate function.
	Combine two unary functions into one with the effect: ( a -- F(a) G(a) ).
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BInt):
		# Bitwise 'and' of two integers
		c = BInt(a.value & b.value)
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, (BNum, BSeq)):
		# Intersection of two sequences
		aa, bb = BType.commonize(a, b)
		cv = []
		if isinstance(aa, BList):
			for v in aa.value:
				if v in bb.value and v not in cv:
					cv.append(v)
		elif isinstance(aa, BStr):
			for v in aa.value:
				if v in bb.value and v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		elif isinstance(aa, BRegex):
			for v in aa.value.pattern:
				if v in bb.value.pattern and v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		else:
			raise BTypeError(self, (a, b))
		c = type(aa)(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Filter sequence by predicate function
		cv = []
		bv = b.simplify().value
		for x in bv:
			context.push(x)
			a.apply(context)
			if context.pop():
				cv.append(x)
		c = BList(cv).convert(b)
		context.push(c)
	elif areinstances((a, b), BFunc):
		# Combine two unary functions ( a -- F(a) G(a) )
		c = BBlock()
		c.value.append(BToken('name', ','))
		c.value.extend(a.convert(BBlock()).value)
		c.value.append(BToken('name', '$'))
		c.value.extend(b.convert(BBlock()).value)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('|', 'Union', 'Map', 'Collect', '¦')
def builtin_bitwise_or_overloaded(self, context, looping=False):
	"""
	Bitwise 'or' of two integers.
	Union of two sequences.
	Map a function onto a sequence.
	Combine two binary functions into one with the effect: ( a b -- F(a,b) G(a,b) ).
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BInt):
		# Bitwise 'or' of two integers
		c = BInt(a.value | b.value)
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, (BNum, BSeq)):
		# Union of two sequences
		aa, bb = BType.commonize(a, b)
		cv = []
		if isinstance(aa, BList):
			for v in aa.value + bb.value:
				if v not in cv:
					cv.append(v)
		elif isinstance(aa, BStr):
			for v in aa.value + bb.value:
				if v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		elif isinstance(aa, BRegex):
			for v in aa.value.pattern + bb.value.pattern:
				if v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		else:
			raise BTypeError(self, (a, b))
		c = type(aa)(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Map function onto sequence
		cv = []
		for x in b.simplify().value:
			n = len(context.stack)
			context.push(x)
			a.apply(context)
			cv.extend(context.pop_till(n))
		context.push(BList(cv))
	elif areinstances((a, b), BFunc):
		# Combine two binary functions: ( a b -- F(a,b) G(a,b) )
		c = BBlock()
		c.value.append(BToken('name', ',t'))
		c.value.extend(a.convert(BBlock()).value)
		c.value.append(BToken('name', '@'))
		c.value.append(BToken('name', '@'))
		c.value.extend(b.convert(BBlock()).value)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('^', 'Diff', 'Difference', 'Filterindexes', '⊖')
def builtin_bitwise_xor_overloaded(self, context, looping=False):
	"""
	Bitwise 'xor' of two integers.
	Exponentiate two numbers (if not two integers).
	Symmetric difference of two sequences.
	Filter a sequence by a predicate function and take the indices.
	Modify a function to repeat a number of times.
	Combine two binary functions into one with the effect: ( a b c d -- F(a,b) G(c,d) ).
	"""
	b = context.pop()
	a = context.pop()
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if areinstances((a, b), BInt):
		# Bitwise 'xor' of two integers
		c = BInt(a.value ^ b.value)
		context.push(c)
	elif areinstances((a, b), BNum):
		# Exponentiate two numbers
		aa, bb = BType.commonize(a, b)
		try:
			cv = aa.value ** bb.value
		except:
			cv = float('nan')
		c = BType.from_python(cv)
		context.push(c)
	elif isinstance(a, BSeq) and isinstance(b, (BNum, BSeq)):
		# Symmetric difference of two sequences
		aa, bb = BType.commonize(a, b)
		cv = []
		if isinstance(aa, BList):
			for v in aa.value:
				if v not in bb.value and v not in cv:
					cv.append(v)
			for v in bb.value:
				if v not in aa.value and v not in cv:
					cv.append(v)
		elif isinstance(aa, BStr):
			for v in aa.value:
				if v not in bb.value and v not in cv:
					cv.append(v)
			for v in bb.value:
				if v not in aa.value and v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		elif isinstance(aa, BRegex):
			for v in aa.value.pattern:
				if v not in bb.value.pattern and v not in cv:
					cv.append(v)
			for v in bb.value.pattern:
				if v not in aa.value.pattern and v not in cv:
					cv.append(v)
			cv = ''.join(cv)
		else:
			raise BTypeError(self, (a, b))
		c = type(aa)(cv)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BNum):
		# Modify function to repeat a number of times
		n = int(b.simplify().value)
		aa = a.convert(BBlock())
		c = BBlock()
		for i in range(n):
			c.value.extend(aa.value)
		context.push(c)
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Filter sequence by predicate function and get indices
		cv = []
		bv = b.simplify().value
		for (i, x) in enumerate(bv):
			context.push(x)
			a.apply(context)
			if context.pop():
				cv.append(BInt(i))
		c = BList(cv).convert(b)
		context.push(c)
	elif areinstances((a, b), BFunc):
		# Combine two binary functions: ( a b c d -- F(a,b) G(c,d) )
		c = BBlock()
		c.value.extend(b.convert(BBlock()).value)
		c.value.append(BToken('name', '@'))
		c.value.append(BToken('name', '@'))
		c.value.extend(a.convert(BBlock()).value)
		c.value.append(BToken('name', '$'))
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('<', 'Less', 'Take', 'Takewhile', '≱')
def builtin_less_than_overloaded(self, context, looping=False):
	"""
	Test two similarly-typed ordered values for less-than order.
	Take the first N items of a sequence.
	Take the first items of a sequence which pass a predicate function.
	"""
	b = context.pop()
	a = context.pop()
	if areinstances((a, b), BReal) or areinstances((a, b), BSeq):
		# Test two similarly-typed ordered values for less-than order
		c = BInt(a < b)
		context.push(c)
		return
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if isinstance(a, BSeq) and isinstance(b, BNum):
		# Take the first N items of a sequence
		i = int(b.simplify().value)
		try:
			if isinstance(a, BRegex):
				pv = a.value.pattern[:i]
				try:
					cv = regex.compile(pv, a.flags)
					c = BRegex(cv)
				except:
					c = BStr(pv)
			else:
				cv = a.value[:i]
				c = type(a)(cv)
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Take the first items of a sequence which pass a predicate function
		cv = []
		bv = b.simplify().value
		for x in bv:
			context.push(x)
			a.apply(context)
			if not context.pop():
				break
			cv.append(x)
		c = BList(cv).convert(b)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('>', 'Greater', 'More', 'Drop', 'Dropwhile', '≰')
def builtin_greater_than_overloaded(self, context, looping=False):
	"""
	Test two similarly-typed ordered values for greater-than order.
	Drop the first N items from a sequence.
	Drop the first items of a sequence which pass a predicate function.
	"""
	b = context.pop()
	a = context.pop()
	if areinstances((a, b), BReal) or areinstances((a, b), BSeq):
		# Test two similarly-typed values ordered for greater-than order
		c = BInt(a > b)
		context.push(c)
		return
	if (isinstance(a, BNum) and not isinstance(b, BNum) or
		isinstance(a, BSeq) and isinstance(b, BFunc)):
		a, b = b, a
	if isinstance(a, BSeq) and isinstance(b, BNum):
		# Drop the first N items from a sequence
		i = int(b.simplify().value)
		try:
			if isinstance(a, BRegex):
				pv = a.value.pattern[i:]
				try:
					cv = regex.compile(pv, a.flags)
					c = BRegex(cv)
				except:
					c = BStr(pv)
			else:
				cv = a.value[i:]
				c = type(a)(cv)
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BFunc) and isinstance(b, BSeq):
		# Drop the first items of a sequence which pass a predicate function
		cv = []
		bv = b.simplify().value
		failed = False
		for x in bv:
			context.push(x)
			a.apply(context)
			if not context.pop():
				failed = True
			if failed:
				cv.append(x)
		c = BList(cv).convert(b)
		context.push(c)
	else:
		raise BTypeError(self, (a, b))

@BBuiltin('_', 'Neg', 'Negate', 'Dump', '∓')
def builtin_negate_overloaded(self, context, looping=False):
	"""
	Negate a number.
	Dump the items of a sequence onto the stack.
	Execute a function in the current scope.
	"""
	a = context.pop()
	if isinstance(a, BNum):
		# Negate number
		context.push(type(a)(-a.value))
	elif isinstance(a, BSeq):
		# Dump sequence
		for x in a.simplify().value:
			context.push(x)
	elif isinstance(a, BFunc):
		# Execute function in current scope
		tokens = a.simplify().value
		context.execute_tokens(tokens)

@BBuiltin('~', 'Flip', 'Conj', 'Conjugate', 'Rev', 'Reverse', 'Conv',
	'Converse', 'Я')
@signature(_)
def builtin_bitwise_negation_overloaded(a):
	"""
	Bitwise negation of an integer.
	Conjugate of a real or complex number.
	Reverse a sequence.
	Converse of a function (prepend '$').
	"""
	if isinstance(a, BInt):
		# Bitwise negation of an integer
		return BInt(~a.value)
	elif isinstance(a, BFloat):
		# Conjugate of a real number (no change)
		return BFloat(a.value)
	elif isinstance(a, BComplex):
		# Conjugate of a complex number
		return BComplex(a.value.conjugate())
	elif isinstance(a, BRegex):
		# Reverse a regex
		pv = a.value.pattern[::-1]
		try:
			return BRegex(regex.compile(pv, a.value.flags))
		except:
			return BStr(rv)
	elif isinstance(a, BSeq):
		# Reverse a sequence
		return type(a)(a.value[::-1])
	elif isinstance(a, BFunc):
		# Converse of a function (prepend '$')
		b = BBlock()
		b.value.append(BToken('name', '$'))
		b.value.extend(a.convert(BBlock()).value)
		return b

@BBuiltin('#', 'Abs', 'Absolute', 'Norm', 'Mag', 'Magnitude', 'Len', 'Length',
	'Commute')
@signature(_)
def builtin_abs_overloaded(a):
	"""
	Absolute value of a number.
	Length of a sequence.
	Commute a function (prepend ',').
	"""
	if isinstance(a, BNum):
		# Absolute value of number
		return type(a)(abs(a.value)).simplify()
	elif isinstance(a, BRegex):
		# Length of regex
		return BInt(len(a.value.pattern))
	elif isinstance(a, BSeq):
		# Length of sequence
		return BInt(len(a.value))
	elif isinstance(a, BFunc):
		# Commute a function (prepend ',')
		b = BBlock()
		b.value.append(BToken('name', ','))
		b.value.extend(a.convert(BBlock()).value)
		return b

@BBuiltin('(', 'Decr', 'Decrement', 'Pred', 'First', 'Uncons', '∇', '₀', '₋')
def builtin_decrement_overloaded(self, context, looping=False):
	"""
	Decrement a number by 1.
	Move the first item of a sequence to the top of the stack.
	Modify an unary function to have the effect: ( a b -- F(a) b ).
	"""
	a = context.pop()
	if isinstance(a, BNum):
		# Decrement a number by 1
		b = type(a)(a.value - 1)
		context.push(b)
	elif isinstance(a, BList):
		# Move the first item of a list to the top of the stack
		try:
			b = a.value.pop(0)
			context.push(a)
			context.push(b)
		except IndexError:
			context.push(a)
	elif isinstance(a, BStr):
		# Move the first character of a string to the top of the stack
		b = BStr(a.value[1:])
		context.push(b)
		try:
			c = a.simplify().value[0]
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BRegex):
		# Move the first character of a regex to the top of the stack
		try:
			bv = regex.compile(a.value.pattern[1:], a.value.flags)
			b = BRegex(bv)
		except:
			b = BStr(a.value.pattern[1:])
		context.push(b)
		try:
			c = a.simplify().value[0]
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BFunc):
		# Modify an unary function: ( a b -- F(a) b )
		b = BBlock()
		b.value.append(BToken('name', '$'))
		b.value.extend(a.convert(BBlock()).value)
		b.value.append(BToken('name', '$'))
		context.push(b)
	else:
		raise BTypeError(self, a)

@BBuiltin(')', 'Incr', 'Increment', 'Succ', 'Last', 'Unrcons', '∆', '₊')
def builtin_increment_overloaded(self, context, looping=False):
	"""
	Increment a number by 1.
	Move the last item of a sequence to the top of the stack.
	Modify an unary function to have the effect: ( a b -- F(a) F(b) ).
	"""
	a = context.pop()
	if isinstance(a, BNum):
		# Increment a number by 1
		b = type(a)(a.value + 1)
		context.push(b)
	elif isinstance(a, BList):
		# Move the last item of a list to the top of the stack
		try:
			b = a.value.pop()
			context.push(a)
			context.push(b)
		except IndexError:
			context.push(a)
	elif isinstance(a, BStr):
		# Move the last character of a string to the top of the stack
		b = BStr(a.value[:-1])
		context.push(b)
		try:
			c = a.simplify().value[-1]
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BRegex):
		# Move the last character of a regex to the top of the stack
		try:
			bv = regex.compile(a.value.pattern[:-1], a.value.flags)
			b = BRegex(bv)
		except:
			b = BStr(a.value.pattern[:-1])
		context.push(b)
		try:
			c = a.simplify().value[-1]
			context.push(c)
		except IndexError:
			pass
	elif isinstance(a, BFunc):
		# Modify an unary function: ( a b -- F(a) F(b) )
		b = BBlock()
		b.value.append(BToken('name', '$'))
		b.value.extend(a.convert(BBlock()).value)
		b.value.extend(b.value)
		context.push(b)
	else:
		raise BTypeError(self, a)

@BBuiltin('H', 'Ri', 'Randint', 'Choice')
@signature((BNum, BSeq))
def builtin_h_overloaded(a):
	"""
	Choose a random integer uniformly in the interval [0, N).
	Choose a random item from a sequence.
	"""
	if isinstance(a, BNum):
		av = int(a.simplify().value)
		return BInt(random.randrange(av))
	elif isinstance(a, BSeq):
		return random.choice(a.simplify().value)

@BBuiltin('U', 'Up', 'Upto', 'Permutations', 'Until', '℗', '₩')
def builtin_u_overloaded(self, context, looping=False):
	"""
	List the integers in the interval [0, N).
	List all permutations of a sequence.
	Apply 'cond'. While popped is false, apply 'body' and 'cond'.
	"""
	a = context.pop()
	if isinstance(a, BNum):
		av = int(a.simplify().value)
		context.push(BList([BInt(i) for i in range(av)]))
	elif isinstance(a, BSeq):
		av = a.simplify().value
		pv = [BList(p).convert(a) for p in itertools.permutations(av)]
		context.push(BList(pv))
	elif isinstance(a, BFunc):
		b = context.pop()
		b.apply(context)
		c = context.pop()
		while not c and not context.broken:
			a.apply(context, looping=True)
			b.apply(context)
			c = context.pop()
		if context.broken != BContext.EXITED:
			context.broken = False

@BBuiltin('E', 'Int', 'Integer', 'Enum', 'Enumerate')
@signature((BNum, BSeq))
def builtin_e_overloaded(a):
	"""
	Convert a number to an integer.
	Pair each item in a sequence with its index.
	"""
	if isinstance(a, BNum):
		return BInt(int(a.simplify().value))
	elif isinstance(a, BSeq):
		# In Birdiescript: ,#U$Z
		av = a.simplify().value
		return BList([BList([BInt(i), x]) for (i, x) in enumerate(av)])

@BBuiltin('L', 'Sh', 'Shuffle', 'Shuffled')
@signature((BNum, BSeq))
def builtin_l_overloaded(a):
	"""
	Randomly shuffle a sequence of all integers in the interval [0, N).
	Randomly shuffle a given sequence.
	"""
	if isinstance(a, BNum):
		av = int(a.simplify().value)
		sv = [BInt(i) for i in range(av)]
		random.shuffle(sv)
		return BList(sv)
	elif isinstance(a, BSeq):
		av = a.simplify().value
		random.shuffle(av)
		return BList(av).convert(a)

@BBuiltin('M', 'Max', 'Maximum', 'Argmax', 'Maxby')
def builtin_m_overloaded(self, context, looping=False):
	"""
	Maximum of two real numbers.
	Maximum of a sequence.
	Argument of the maximum of two numbers by a key function.
	Argument of the maximum of a sequence by a key function.
	"""
	a = context.pop()
	if isinstance(a, BReal):
		# In Birdiescript: ,t<@nIu
		b = context.pop()
		if not isinstance(b, BReal):
			raise BTypeError(self, (b, a))
		context.push(max(b, a))
	elif isinstance(a, BSeq):
		# In Birdiescript: {,t<@nI}*
		context.push(max(a.simplify().value))
	elif isinstance(a, BFunc):
		b = context.pop()
		if isinstance(b, BNum):
			c = context.pop()
			if not isinstance(c, BNum):
				raise BTypeError(self, (c, b, a))
			context.push(c)
			a.apply(context)
			ck = context.pop()
			context.push(b)
			a.apply(context)
			bk = context.pop()
			d = {ck: c, bk: b}
			context.push(d[max(ck, bk)])
		elif isinstance(b, BSeq):
			# In Birdiescript: '?|?#U@ZtM)p'
			bv = b.simplify().value
			d = {}
			for (i, x) in enumerate(bv):
				context.push(x)
				a.apply(context)
				xk = context.pop()
				d[x] = (xk, i)
			context.push(max(bv, key=lambda x: d[x]))
		else:
			raise BTypeError(self, (b, a))
	else:
		raise BTypeError(self, a)

@BBuiltin('N', 'Min', 'Minimum', 'Argmin', 'Minby')
def builtin_n_overloaded(self, context, looping=False):
	"""
	Minimum of two real numbers.
	Minimum of a sequence.
	Argument of the minimum of two numbers by a key function.
	Argument of the minimum of a sequence by a key function.
	"""
	a = context.pop()
	if isinstance(a, BReal):
		# In Birdiescript: ,t>@nIu
		b = context.pop()
		if not isinstance(b, BReal):
			raise BTypeError(self, (b, a))
		context.push(min(b, a))
	elif isinstance(a, BSeq):
		# In Birdiescript: {,t>@nI}*
		context.push(min(a.simplify().value))
	elif isinstance(a, BFunc):
		b = context.pop()
		if isinstance(b, BNum):
			c = context.pop()
			if not isinstance(c, BNum):
				raise BTypeError(self, (c, b, a))
			context.push(c)
			a.apply(context)
			ck = context.pop()
			context.push(b)
			a.apply(context)
			bk = context.pop()
			d = {ck: c, bk: b}
			context.push(d[min(ck, bk)])
		elif isinstance(b, BSeq):
			# In Birdiescript: '?|?#U@ZtN)p'
			bv = b.simplify().value
			d = {}
			for (i, x) in enumerate(bv):
				context.push(x)
				a.apply(context)
				xk = context.pop()
				d[x] = (xk, i)
			context.push(min(bv, key=lambda x: d[x]))
		else:
			raise BTypeError(self, (b, a))
	else:
		raise BTypeError(self, a)

@BBuiltin('Q', 'Sqrt', 'Uniq', 'Unique', 'Nub', '√')
@signature((BNum, BSeq))
def builtin_q_overloaded(a):
	"""
	Square root of a number.
	Remove duplicate values from a sequence.
	"""
	if isinstance(a, BNum):
		# In Birdiescript: .5^p
		return BType.from_python(cmath.sqrt(a.value)).simplify()
	elif isinstance(a, BSeq):
		# In Birdiescript: ,|
		av = a.simplify().value
		uv = []
		for x in av:
			if x not in uv:
				uv.append(x)
		return BList(uv).convert(a)

@BBuiltin('S', 'Sin', 'Sine', 'Sort', 'Sortby')
def builtin_s_overloaded(self, context, looping=False):
	"""
	Sine function of a number.
	Sort a sequence.
	Sort a sequence by a key function.
	"""
	a = context.pop()
	if isinstance(a, BNum):
		context.push(BType.from_python(cmath.sin(a.value)).simplify())
	elif isinstance(a, BSeq):
		av = a.simplify().value
		av.sort()
		context.push(BList(av).convert(a))
	elif isinstance(a, BFunc):
		# In Birdiescript: ?|?#U@ZtS\\)p|
		b = context.pop()
		if not isinstance(b, BSeq):
			raise BTypeError(self, (b, a))
		bv = b.simplify().value
		d = {}
		for (i, x) in enumerate(bv):
			context.push(x)
			a.apply(context)
			xk = context.pop()
			d[x] = (xk, i)
		bv.sort(key=lambda x: d[x])
		context.push(BList(bv).convert(b))

@BBuiltin('C', 'Cos', 'Cosine', 'Combinations', 'Powerset', '©')
@signature((BNum, BSeq))
def builtin_c_overloaded(a):
	"""
	Cosine function of a number.
	Power set of a sequence.
	"""
	if isinstance(a, BNum):
		return BType.from_python(cmath.cos(a.value)).simplify()
	elif isinstance(a, BSeq):
		# In Birdiescript: [[]]{\++?|+}@-
		av = a.simplify().value
		cv = [BList(c).convert(a) for c in itertools.chain.from_iterable(
			itertools.combinations(av, i) for i in range(len(av)+1))]
		return BList(cv)

@BBuiltin('T', 'Tan', 'Tangent', 'Transpose', 'Unzip', '™', 'ᵀ')
@signature((BNum, BList))
def builtin_t_overloaded(a):
	"""
	Tangent function of a number.
	Transpose a list of sequences.
	"""
	if isinstance(a, BNum):
		return BType.from_python(cmath.tan(a.value)).simplify()
	elif isinstance(a, BList):
		if not a.value:
			return BList()
		s = min(a.value, key=lambda x: x.rank)
		avv = [x.simplify().value for x in a.value]
		tv = [BList(xv).convert(s) for xv in zip(*avv)]
		return BList(tv)

@BBuiltin('Z', 'Precision', 'Zip')
def builtin_z_overloaded(self, context, looping=False):
	"""
	Round a number to a given level of precision.
	Zip two sequences together.
	"""
	b = context.pop()
	a = context.pop()
	if areinstances((a, b), BReal):
		context.push(BFloat(round(a.value, b.simplify().value)))
	elif areinstances((a, b), BSeq):
		# In Birdiescript: ]pT
		s = min(a, b, key=lambda x: x.rank)
		av = a.simplify().value
		bv = b.simplify().value
		zv = [BList(zx).convert(s) for zx in zip(av, bv)]
		context.push(BList(zv))
	else:
		raise BTypeError(self, (a, b))


#################### Arithmetic operations ####################

@BBuiltin('/i', '÷i', 'Intdiv', '†', code='/E')
@signature(BNum, BNum)
def builtin_intdiv(a, b):
	"""Divide two numbers and take the integer part."""
	aa, bb = BType.commonize(a, b)
	try:
		cv = aa.value // bb.value
	except:
		cv = float('nan')
	return BType.from_python(cv)

BBuiltin('Nv', 'Inv', 'Inverse', 'Reciprocal', '⅟', 'И', code='1$/',
	doc="""Reciprocal (multiplicative inverse) of a number.""")

@BBuiltin('/m', '÷m', 'Divmod', '‡')
@signature(BNum, BNum)
def builtin_divmod(a, b):
	"""Get (X-X%Y)/Y and X%Y for numbers X and Y."""
	aa, bb = BType.commonize(a, b)
	dv, mv = divmod(aa.value, bb.value)
	d = type(aa)(dv)
	m = type(aa)(mv)
	return (d, m)

BBuiltin('Prop', '∝', '∣', code='%!',
	doc="""Test whether a number evenly divides another number.""")
BBuiltin('Nprop', '∤', code='%!!',
	doc="""Test whether a number does not evenly divide another number.""")

BBuiltin('Ev', 'Even', code='2%!', doc="""Test whether a number is even.""")
BBuiltin('Od', code='2%!!', doc="""Test whether a number is odd.""")

@BBuiltin('^p', 'Pow', 'Power')
@signature(BNum, BNum)
def builtin_exponent(a, b):
	"""Exponentiate two numbers."""
	aa, bb = BType.commonize(a, b)
	try:
		cv = aa.value ** bb.value
	except:
		cv = float('nan')
	return BType.from_python(cv)

# Superscript numerals
BBuiltin('⁰', code='0^p', doc="""Raise a number to the 0th power.""")
BBuiltin('¹', code='1^p', doc="""Raise a number to the 1st power.""")
BBuiltin('Sq', 'Square', '²', code='2^p',
	doc="""Raise a number to the 2nd power (square it).""")
BBuiltin('Cb', 'Cube', '³', code='3^p',
	doc="""Raise a number to the 3rd power (cube it).""")
BBuiltin('⁴', code='4^p', doc="""Raise a number to the 4th power.""")
BBuiltin('⁵', code='5^p', doc="""Raise a number to the 5th power.""")
BBuiltin('⁶', code='6^p', doc="""Raise a number to the 6th power.""")
BBuiltin('⁷', code='7^p', doc="""Raise a number to the 7th power.""")
BBuiltin('⁸', code='8^p', doc="""Raise a number to the 8th power.""")
BBuiltin('⁹', code='9^p', doc="""Raise a number to the 9th power.""")

@BBuiltin('Qr', 'Root', 'Surd')
@signature(BNum, BNum)
def builtin_root(a, n):
	"""Nth root of a number."""
	try:
		rv = a.value ** (1 / n.value)
	except:
		rv = cmath.exp(n.value * cmath.log(a.value))
	return BType.from_python(rv)

BBuiltin('Cubert', '∛', code='3Qr',
	doc="""Cube root of a number.""")
BBuiltin('Fourthrt', '∜', code='4Qr',
	doc="""Fourth root of a number.""")

BBuiltin('=c', 'Cmp', 'Compare', '≶', '≷', '⋈', '⋚', '⋛', code=',t>@n<-',
	doc="""Compare ordering of two values (+1, 0, or -1).""")

BBuiltin('Nr', 'Num', 'Number', 'Parsenum', '№',
	code=r"Stw,`^-?(?:[0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+)(?:[Ee]-?[0-9]+)?$`~m{,'-^s{(;X_}\XI}\NanI",
	doc="""Parse a string as a decimal number, optionally in scientific notation.""")

BBuiltin('Sg', 'Sgn', 'Sign', code=",#,\\/\\;pI",
	doc="""Sign of a number (N / |N|).""")

BBuiltin('Ir', 'Inrange', code=',@<@n>!&',
	doc="""Test whether a number is in an interval [A, B).""")

@BBuiltin('Er', 'Round')
@signature(BNum)
def builtin_round(n):
	"""Round a number to the nearest integer."""
	if isinstance(n, BInt):
		return n
	elif isinstance(n, BFloat):
		return BFloat(round(n.value))
	elif isinstance(n, BComplex):
		nv = n.value
		return BComplex(complex(round(nv.real), round(nv.imag)))

@BBuiltin('Fl', 'Floor', '⌊')
@signature(BNum)
def builtin_floor(n):
	"""Floor function. Round a number downward."""
	if isinstance(n, BInt):
		return n
	elif isinstance(n, BFloat):
		return BFloat(math.floor(n.value))
	elif isinstance(n, BComplex):
		nv = n.value
		return BComplex(complex(math.floor(nv.real),
			math.floor(nv.imag)))

@BBuiltin('Cl', 'Ceil', 'Ceiling', '⌈')
@signature(BNum)
def builtin_ceiling(n):
	"""Ceiling function. Round a number upward."""
	if isinstance(n, BInt):
		return n
	elif isinstance(n, BFloat):
		return BFloat(math.ceil(n.value))
	elif isinstance(n, BComplex):
		nv = n.value
		return BComplex(complex(math.ceil(nv.real), math.ceil(nv.imag)))

@BBuiltin('Gcd', 'Gcf')
@signature(BNum, BNum)
def builtin_gcd(a, b):
	"""Greatest common denominator/factor of two numbers."""
	aa, bb = BType.commonize(a, b)
	av, bv = aa.value, bb.value
	if areinstances((aa, bb), BComplex):
		# GCD of two complex numbers (Gaussian integers)
		a1, b1 = 1, 0
		a2, b2 = 0, 1
		if abs(bv) > abs(av):
			av, bv = bv, av
			a1, b1, a2, b2 = a2, b2, a1, b1
		while True:
			q = av / bv
			q = complex(int(round(q.real)), int(round(q.imag)))
			av -= bv * q
			a1 -= q * a2
			b1 -= q * b2
			if not av:
				return BType.from_python(bv).simplify()
			q = bv / av
			q = complex(int(round(q.real)), int(round(q.imag)))
			bv -= av * q
			a2 -= q * a1
			b2 -= q * b1
			if not bv:
				return BType.from_python(av).simplify()
	# GCD of two real numbers (integers)
	while bv:
		av, bv = bv, av % bv
	return BFloat(av).simplify()

BBuiltin('Lcm', code=",t*#@nGcd,'/';pI",
	doc="""Least common multiple of two numbers.""")

BBuiltin('Cpr', 'Coprime', code='Gcd1=',
	doc="""Test if two numbers are coprime.""")

@BBuiltin('Pp', 'Isprime')
@signature(BNum)
def builtin_isprime(n):
	"""Test whether a number is prime."""
	# Adapted from implementations on Rosetta Code
	# <http://rosettacode.org/wiki/Primality_by_trial_division>
	if not isinstance(n, BInt) or n.value <= 1:
		return BInt(0)
	nv = n.value
	if nv == 2 or nv == 3 or nv == 5:
		return BInt(1)
	if not nv % 2 or not nv % 3 or not nv % 5:
		return BInt(0)
	for i in range(7, int(math.sqrt(nv))+1, 30):
		if not nv % i: return BInt(0)
		if not nv % (i + 4): return BInt(0)
		if not nv % (i + 6): return BInt(0)
		if not nv % (i + 10): return BInt(0)
		if not nv % (i + 12): return BInt(0)
		if not nv % (i + 16): return BInt(0)
		if not nv % (i + 22): return BInt(0)
		if not nv % (i + 24): return BInt(0)
	return BInt(1)

@BBuiltin('Pu', 'Primesupto', code='U\\Pp&')
@signature(BNum)
def builtin_primes_upto(n):
	"""List the prime numbers below N."""
	# Optimized implementation by Robert William Hanks
	# <http://stackoverflow.com/a/3035188/70175>
	nv = n.value
	if nv <= 2: return BList([])
	if nv <= 3: return BList([BInt(2)])
	if nv <= 5: return BList([BInt(2), BInt(3)])
	nv, c = nv-nv%6+6, 2-(nv%6>1)
	sieve = [True] * (nv // 3)
	for i in range(1, int(math.sqrt(nv))//3+1):
		if sieve[i]:
			k = 3*i+1 | 1
			sieve[k*k//3::2*k] = [False] * ((nv//6-k*k//6-1)//k+1)
			sieve[k*(k-2*(i&1)+4)//3::2*k] = ([False] *
				((nv//6-k*(k-2*(i&1)+4)//6-1)//k+1))
	return BList([BInt(2), BInt(3)] + [BInt(3*i+1|1) for i in
		range(1, nv//3-c) if sieve[i]])

@BBuiltin('Np', 'Nprimes')
@signature(BNum)
def builtin_n_primes(n):
	"""List the first N prime numbers."""
	ps = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
		61, 67, 71, 73, 79, 83, 89, 97]
	nv = n.simplify().value
	c = ps[-1] + 2
	while len(ps) < nv:
		if c % 2 and c % 3 and c % 5:
			for i in range(7, int(math.sqrt(c))+1, 30):
				if not c % i: break
				if not c % (i + 4): break
				if not c % (i + 6): break
				if not c % (i + 10): break
				if not c % (i + 12): break
				if not c % (i + 16): break
				if not c % (i + 22): break
				if not c % (i + 24): break
			else:
				ps.append(c)
		c += 2
	return BList([BInt(p) for p in ps[:nv]])

@BBuiltin('Fp', 'Factor')
@signature(BNum)
def builtin_factor(n):
	"""Prime factorization of a number."""
	if isinstance(n, (BFloat, BComplex)) or n.value <= 1:
		return BList([n])
	gaps = [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6]
	period = len(gaps)
	cycle = 3
	fs, f, i, k = [], 2, 0, n.value
	while f * f <= k:
		while not k % f:
			fs.append(BInt(f))
			k //= f
		f += gaps[i]
		i += 1
		if i == period:
			i = cycle
	if k > 1: fs.append(BInt(k))
	if len(fs) == 1: fs.append(BInt(1))
	if not fs: fs.append(n)
	return BList(fs)

@BBuiltin('B', 'Base')
@signature((BReal, BSeq), BInt)
def builtin_base(n, b):
	"""Convert a number to a sequence of digits in a base, or vice-versa."""
	if b.value < 2:
		raise ValueError('cannot convert to base < 2: {}'.format(b))
	if isinstance(n, BInt):
		# Convert an integer to a list of place values
		nv, bv = n.value, b.value
		neg = nv < 0
		if neg:
			nv = -nv
		dv = []
		while nv:
			dv.insert(0, BInt(nv % bv))
			nv //= bv
		if neg:
			dv.insert(0, BStr('-'))
		return BList(dv)
	elif isinstance(n, BFloat):
		# Convert a floating point number to a list of place values
		bv = b.value
		neg = n.value < 0
		if neg:
			n.value = -n.value
		nf, ni = math.modf(n.value)
		ni = int(ni)
		dv = []
		while ni:
			dv.insert(0, BInt(ni % bv))
			ni //= bv
		dv.append(BStr('.'))
		tn = len(repr(nf).split('.')[-1]) * math.log(10, bv)
		t = 0
		while nf and t < tn:
			k = int(math.floor(bv * nf))
			dv.append(BInt(k))
			nf = math.modf(nf * bv)[0]
			t += 1
		if neg:
			dv.insert(0, BStr('-'))
		return BList(dv)
	elif isinstance(n, BSeq):
		# Convert a list of place values to a number
		dv = n.simplify().value[:]
		neg = dv[0] == BStr('-')
		if neg:
			dv = dv[1:]
		if BStr('.') in dv:
			# Convert a list of place values to a floating point number
			dp = dv.index(BStr('.'))
			nv = 0.0
			p = 0
			for i in range(dp-1, -1, -1):
				d = dv[i]
				if not isinstance(d, BInt):
					msg = 'not a digit value: {}'.format(d)
					raise ValueError(msg)
				nv += d.value * b.value ** p
				p += 1
			
			p = -1
			for i in range(dp+1, len(dv)):
				d = dv[i]
				if not isinstance(d, BInt):
					msg = 'not a digit value: {}'.format(d)
					raise ValueError(msg)
				nv += d.value * b.value ** p
				p -= 1
			if neg:
				nv = -nv
			return BFloat(nv)
		else:
			# Convert a list of place values to an integer
			nv = 0
			p = 0
			while dv:
				d = dv.pop()
				if not isinstance(d, BInt):
					msg = 'not a digit value: {}'.format(d)
					raise ValueError(msg)
				nv += d.value * b.value ** p
				p += 1
			if neg:
				nv = -nv
			return BInt(nv)

BBuiltin('Bb', 'Bin', 'Binary', '₂', code='2B',
	doc="""Convert a number to a sequence of digits in base 2, or vice-versa.""")
BBuiltin('Bt', 'Ter', 'Ternary', '₃', code='3B',
	doc="""Convert a number to a sequence of digits in base 3, or vice-versa.""")
BBuiltin('Bq', 'Qua', 'Quaternary', '₄', code='4B',
	doc="""Convert a number to a sequence of digits in base 4, or vice-versa.""")
BBuiltin('Bo', 'Oct', 'Octal', '₈', code='8B',
	doc="""Convert a number to a sequence of digits in base 8, or vice-versa.""")
BBuiltin('Bd', 'Dec', 'Decimal', code='10B',
	doc="""Convert a number to a sequence of digits in base 10, or vice-versa.""")
BBuiltin('Bx', 'Hex', 'Hexadecimal', 'ₓ', 'ₕ', code='16B',
	doc="""Convert a number to a sequence of digits in base 16, or vice-versa.""")

BBuiltin('Bc', 'Baseconv', 'Baseconvert', code='@nB$B',
	doc="""Convert a sequence of digits from one base to another.""")

@BBuiltin('Ba', 'Baseascii')
@signature((BReal, BSeq), BInt)
def builtin_base_ascii(n, b):
	"""Convert a number to a sequence of ASCII digits in a base, or vice-versa."""
	ds = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!"#$%&\'()*+,-./:;<=>?@[]^_{|}~\\`'
	maxb = len(ds)
	if not 2 <= b.value <= maxb:
		msg = 'cannot convert to base < 2 or > {}: {}'.format(maxb, b)
		raise ValueError(msg)
	if isinstance(n, BInt):
		# Convert an integer to a string of digits
		nv, bv = n.value, b.value
		neg = nv < 0
		if neg:
			nv = -nv
		dv = []
		while nv:
			dv.insert(0, ds[nv % bv])
			nv //= bv
		if neg:
			dv.insert(0, '-')
		return BStr(''.join(dv))
	elif isinstance(n, BFloat):
		# Convert a floating point number to a string of digits
		nv, bv = n.value, b.value
		neg = n.value < 0
		if neg:
			nv = -nv
		nf, ni = math.modf(nv)
		ni = int(ni)
		dv = []
		while ni:
			dv.insert(0, ds[ni % bv])
			ni //= bv
		dv.append('.')
		tn = len(repr(nf).split('.')[-1]) * math.log(10, bv)
		t = 0
		while nf and t < tn:
			k = int(math.floor(bv * nf))
			dv.append(ds[k])
			nf = math.modf(nf * bv)[0]
			t += 1
		if neg:
			dv.insert(0, '-')
		return BStr(''.join(dv))
	elif isinstance(n, BSeq):
		# Convert a string of digits to a number
		ds = {d: i for (i, d) in enumerate(ds)}
		dv = n.convert(BStr()).value
		if b.value <= 36:
			dv = dv.upper()
		neg = dv[0] == '-'
		if neg:
			dv = dv[1:]
		if '.' in dv and b.value <= ds['.']:
			# Convert a string of digits to a floating point number
			dp = dv.index('.')
			nv = 0.0
			p = 0
			for i in range(dp-1, -1, -1):
				d = dv[i]
				if d not in ds:
					msg = 'not a digit value: {}'.format(
						repr(d))
					raise ValueError(msg)
				nv += ds[d] * b.value ** p
				p += 1
			p = -1
			for i in range(dp+1, len(dv)):
				d = dv[i]
				if d not in ds:
					msg = 'not a digit value: {}'.format(
						repr(d))
					raise ValueError(msg)
				nv += ds[d] * b.value ** p
				p -= 1
			if neg:
				nv = -nv
			return BFloat(nv)
		else:
			# Convert a string of digits to an integer
			nv = 0
			p = 0
			for i in range(len(dv)-1, -1, -1):
				d = dv[i]
				if d not in ds:
					msg = 'not a digit value: {}'.format(
						repr(d))
					raise ValueError(msg)
				nv += ds[d] * b.value ** p
				p += 1
			if neg:
				nv = -nv
			return BInt(nv)

BBuiltin('Bba', 'Binascii', 'Binaryascii', '₂a', code='2Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 2, or vice-versa.""")
BBuiltin('Bta', 'Terascii', 'Ternaryascii', '₃a', code='3Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 3, or vice-versa.""")
BBuiltin('Bqa', 'Quaascii', 'Quaternaryascii', '₄a', code='4Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 4, or vice-versa.""")
BBuiltin('Boa', 'Octascii', 'Octalascii', '₈a', code='8Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 8, or vice-versa.""")
BBuiltin('Bda', 'Decascii', 'Decimalascii', code='10Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 10, or vice-versa.""")
BBuiltin('Bxa', 'Hexascii', 'Hexadecimalascii', 'ₓa', 'ₕa', code='16Ba',
	doc="""Convert a number to a sequence of ASCII digits in base 16, or vice-versa.""")

BBuiltin('Bac', 'Baseconvascii', 'Baseconvertascii', code='@nBa$Ba',
	doc="""Convert a sequence of ASCII digits from one base to another.""")

@BBuiltin('#p', 'Npr', 'Numpermutations')
@signature(BInt, BInt)
def builtin_npr(n, r):
	"""Number of ways to permute R items from a set of N items."""
	nv, rv = n.value, r.value
	if nv < 0 or rv < 0:
		msg = 'Values must be positive: {} P {}'.format(nv, rv)
		raise ValueError(msg)
	if rv > nv:
		return BInt(0)
	pv, dv = 1, nv - rv
	while nv > dv:
		pv *= nv
		nv -= 1
	return BInt(pv)

@BBuiltin('#c', 'Ncr', 'Numcombinations')
@signature(BInt, BInt)
def builtin_ncr(n, r):
	"""Number of ways to choose R items from a set of N items."""
	nv, rv = n.value, r.value
	if nv < 0 or rv < 0:
		msg = 'Values must be positive: {} C {}'.format(nv, rv)
		raise ValueError(msg)
	if rv > nv:
		return BInt(0)
	cv, dv, kv = 1, max(rv, nv-rv), min(rv, nv-rv)
	while nv > dv:
		cv *= nv
		nv -= 1
	while kv > 1:
		cv /= kv
		kv -= 1
	return BInt(cv)


#################### Bitwise operations ####################

@BBuiltin('<s', '<shift', 'Lshift', '«', '≪')
@signature(BInt, BInt)
def builtin_bitwise_left_shift(a, b):
	"""Bitwise left shift of two integers."""
	return BInt(a.value << b.value)

@BBuiltin('>s', '>shift', 'Rshift', '»', '≫')
@signature(BInt, BInt)
def builtin_bitwise_right_shift(a, b):
	"""Bitwise right shift of two integers."""
	return BInt(a.value >> b.value)

@BBuiltin('>l', '>shiftl', 'Rshiftl')
@signature(BInt, BInt)
def builtin_bitwise_right_logical_shift(a, b):
	"""Bitwise right logical shift of two integers."""
	return BInt((a.value % 0x100000000) >> b.value)


#################### Boolean operations ####################

@BBuiltin('=', 'Eq', 'Equal', '≈', '≅')
@signature(_, _)
def builtin_equal(a, b):
	"""Test two values for equality."""
	if (areinstances((a, b), BNum) or areinstances((a, b), BSeq) or
		areinstances((a, b), BFunc)):
		return BInt(a == b)
	return BInt(0)

@BBuiltin('=s', 'Eqs', 'Equalstrict')
@signature(_, _)
def builtin_strict_equal(a, b):
	"""Test two values for strict equality."""
	return BInt(a.rank == b.rank and a == b)

BBuiltin('=n', 'Neq', '≠', '≉', '≆', code='=!',
	doc="""Test two values for inequality.""")

BBuiltin('=sn', 'Neqs', '≠s', code='=s!',
	doc="""Test two values for strict inequality.""")

BBuiltin('Lesseq', '≤', '≯', code='>!',
	doc="""Test two similarly-typed ordered values for less-than-equal order.""")

BBuiltin('Greatereq', 'Moreeq', '≥', '≮', code='<!',
	doc="""Test two similarly-typed ordered values for greater-than-equal order.""")

@BBuiltin('!', 'Not', '¬')
@signature(_)
def builtin_not(a):
	"""Boolean negation."""
	return BInt(not a)

BBuiltin('Bl', 'Bool', '¡', '‼', code='!!',
	doc="""Convert to a Boolean value. 0 [] `` are false, all else are true.""")

BBuiltin('&l', 'And', '∧', code='?I',
	doc="""Boolean 'and'. Lazily evaluates the second argument.""")
BBuiltin('|l', 'Or', '∨', code='?$I',
	doc="""Boolean 'or'. Lazily evaluates the second argument.""")
BBuiltin('^l', 'Xor', '⊻', '⊕', '≢', code='!$!=!',
	doc="""Boolean 'xor'.""")
BBuiltin('&n', 'Nand', '⊼', '↑', code='&l!',
	doc="""Boolean 'nand'. Lazily evaluates the second argument.""")
BBuiltin('|n', 'Nor', '⊽', '↓', code='&|!',
	doc="""Boolean 'nor'. Lazily evaluates the second argument.""")
BBuiltin('^n', 'Xnor', 'Eqv', '↔', '⇔', '≡', code='^l!',
	doc="""Boolean 'xnor'.""")
BBuiltin('Imp', 'Impl', 'Implies', '→', '⇒', '∴', code='$!$?$I',
	doc="""Boolean implication. Lazily evaluates the second argument.""")
BBuiltin('Impr', 'Implied', '←', '⇐', '∵', code='!$?$I',
	doc="""Boolean converse implication. Lazily evaluates the first argument.""")
BBuiltin('Nimp', 'Nimpl', 'Nonimplies', '↛', code='?!$I',
	doc="""Boolean nonimplication. Lazily evaluates the second argument.""")
BBuiltin('Nimpr', 'Nonmplied', '↚', code='$?!$I',
	doc="""Boolean converse nonimplication. Lazily evaluates the first argument.""")

BBuiltin('True', '⊤', '⊨', value=BInt(1),
	doc="""Canonical true Boolean value (1).""")
BBuiltin('False', '⊥', '⊭', value=BInt(0),
	doc="""Canonical false Boolean value (0).""")


#################### Floating point operations ####################

BBuiltin('Ft', 'Float', 'Complex', code='1.*',
	doc="""Convert a number to floating point.""")

@BBuiltin('?i', 'Isinf')
@signature(BNum)
def builtin_isinf(x):
	"""Test whether a number is infinite."""
	return BInt(cmath.isinf(x.value))

@BBuiltin('?n', 'Isnan')
@signature(BNum)
def builtin_isnan(x):
	"""Test whether a number is NaN (not a number)."""
	return BInt(cmath.isnan(x.value))

@BBuiltin('Fx', 'Floatcast')
@signature(BReal)
def builtin_float_cast(x):
	"""Interpret a floating point value as an integer, or vice-versa."""
	if isinstance(x, BInt):
		fv = struct.unpack(b'>f', struct.pack(b'>l', x.value))[0]
		return BFloat(fv)
	elif isinstance(x, BFloat):
		iv = struct.unpack(b'>l', struct.pack(b'>f', x.value))[0]
		return BInt(iv)

@BBuiltin('Fme', 'Fmantexp')
@signature(BReal)
def builtin_mantissa_exponent(x):
	"""Mantissa and exponent of N such that N = M * 2^E."""
	return tuple(map(BFloat, math.frexp(x.value)))

@BBuiltin('Ffi', 'Ffracint')
@signature(BReal)
def builtin_frac_int(x):
	"""Fractional and integer parts of a floating point number."""
	return tuple(map(BFloat, math.modf(x.value)))

BBuiltin('Fe', 'Fε', 'Fϵ', 'Epsilon', value=BFloat(sys.float_info.epsilon),
	doc="""Floating point machine epsilon.""")
BBuiltin('Fmin', value=BFloat(sys.float_info.min),
	doc="""Minimum positive floating point value.""")
BBuiltin('Fmax', value=BFloat(sys.float_info.max),
	doc="""Maximum floating point value.""")
BBuiltin('Fradix', value=BInt(sys.float_info.radix),
	doc="""Radix of floating point exponents.""")
BBuiltin('Frounds', value=BInt(sys.float_info.rounds),
	doc="""Rounding mode used for floating point arithmetic operations.""")
BBuiltin('Fdig', value=BInt(sys.float_info.dig),
	doc="""Maximum number of decimal digits in a float.""")
BBuiltin('Fmdig', 'Fmantdig', value=BInt(sys.float_info.mant_dig),
	doc="""Number of base-radix digits in a float's mantissa.""")
BBuiltin('Fminexp', value=BInt(sys.float_info.min_exp),
	doc="""Minimum floating point exponent.""")
BBuiltin('Fmaxexp', value=BInt(sys.float_info.max_exp),
	doc="""Maximum floating point exponent.""")
BBuiltin('Fmintenexp', value=BInt(sys.float_info.min_10_exp),
	doc="""Minimum floating point exponent with base 10.""")
BBuiltin('Fmaxtenexp', value=BInt(sys.float_info.max_10_exp),
	doc="""Maximum floating point exponent with base 10.""")


#################### Complex number functions ####################

@BBuiltin('Cr', 'Real')
@signature(BNum)
def builtin_real(x):
	"""Real part of a complex number."""
	return BFloat(x.convert(BComplex()).value.real)

@BBuiltin('Ci', 'Imag')
@signature(BNum)
def builtin_imag(x):
	"""Imaginary part of a complex number."""
	return BFloat(x.convert(BComplex()).value.imag)

@BBuiltin('Ca', 'Arg', 'Argument', 'Phase')
@signature(BNum)
def builtin_arg(x):
	"""Argument (or phase) of a complex number."""
	return BFloat(cmath.phase(x.value))

@BBuiltin('Cp', 'Polar')
@signature(BNum)
def builtin_polar(x):
	"""Polar coordinates R and Phi of a complex number."""
	rv, pv = cmath.polar(x.value)
	return (BFloat(rv), BFloat(phiv))

@BBuiltin('Cc', 'Rect', 'Cartesian')
@signature(BReal, BReal)
def builtin_cartesian(r, phi):
	"""Complex number of polar coordinates R and Phi."""
	return BComplex(cmath.rect(r.value, phi.value))


#################### Algebraic functions ####################

@BBuiltin('Lg', 'Log')
@signature(BNum, BNum)
def builtin_log(x, b):
	"""Logarithm of a number to a base."""
	return BType.from_python(cmath.log(x.value, b.value)).simplify()

@BBuiltin('Ln', 'Lognatural')
@signature(BNum)
def builtin_ln(x):
	"""Natural logarithm of a number (base e)."""
	return BType.from_python(cmath.log(x.value)).simplify()

@BBuiltin('Lc', 'Logcommon')
@signature(BNum)
def builtin_log10(x):
	"""Common logarithm of a number (base 10)."""
	return BType.from_python(cmath.log10(x.value)).simplify()

BBuiltin('Lb', 'Logbinary', code='2Lg',
	doc="""Binary logarithm of a number (base 2).""")

@BBuiltin('Lp', 'Logp')
@signature(BNum)
def builtin_log1p(x):
	"""log(X+1) for a real number X."""
	return BFloat(math.log1p(x.value))

@BBuiltin('Ep', 'Exp')
@signature(BNum)
def builtin_exp(x):
	"""Exponential value e^X of a number X."""
	return BType.from_python(cmath.exp(x.value)).simplify()

@BBuiltin('!f', 'Fac', 'Factorial')
@signature(BNum)
def builtin_factorial(n):
	"""Factorial function."""
	if isinstance(n, BInt):
		nv = n.value
		acc = 1
		while nv > 1:
			acc *= nv
			nv -= 1
		return BInt(acc)
	elif isinstance(n, BFloat):
		return BFloat(math.gamma(n.value + 1))
	return BComplex(complex_gamma(n.value + 1))

@BBuiltin('Ga', 'Gamma', 'Γ')
@signature(BNum)
def builtin_gamma(x):
	"""Gamma function of a real number."""
	if isinstance(x, BReal):
		return BFloat(math.gamma(x.value))
	return BComplex(complex_gamma(x.value))

@BBuiltin('Gl', 'Lgamma', 'Γl')
@signature(BNum)
def builtin_log_gamma(x):
	"""log(|Gamma(X)|) of a real number X."""
	if isinstance(x, BReal):
		return BFloat(math.lgamma(x.value))
	return BComplex(cmath.log(complex_gamma(x.value)))

@BBuiltin('Erf', 'Error')
@signature(BReal)
def builtin_erf(x):
	"""Error function of a real number."""
	return BFloat(math.erf(x.value))

@BBuiltin('Erfc', 'Cerror')
@signature(BReal)
def builtin_erfc(x):
	"""Complementary error function of a real number."""
	return BFloat(math.erfc(x.value))


#################### Trigonometric functions ####################

@BBuiltin('Rad', 'Radians', 'Degtorad', '㎭', 'ʳ')
@signature(BReal)
def builtin_radians(deg):
	"""Convert a number from degrees to radians."""
	return BFloat(math.radians(deg.value)).simplify()

@BBuiltin('Deg', 'Degrees', 'Radtodeg', '°')
@signature(BReal)
def builtin_degrees(rad):
	"""Convert a number from radians to degrees."""
	return BFloat(math.degrees(rad.value)).simplify()

@BBuiltin('Asn', 'Asin', 'Arcsine')
@signature(BNum)
def builtin_asin(x):
	"""Arc sine function."""
	return BType.from_python(cmath.asin(x.value)).simplify()

@BBuiltin('Acs', 'Acos', 'Arccosine')
@signature(BNum)
def builtin_acos(x):
	"""Arc cosine function."""
	return BType.from_python(cmath.acos(x.value)).simplify()

@BBuiltin('Atn', 'Atan', 'Arctangent')
@signature(BNum)
def builtin_atan(x):
	"""Arc tangent function."""
	return BType.from_python(cmath.atan(x.value)).simplify()

@BBuiltin('Att', 'Atantwo')
@signature(BReal, BReal)
def builtin_atan2(y, x):
	"""Arc tangent function of a numerator and denominator."""
	return BFloat(math.atan2(y.value, x.value))

@BBuiltin('Snh', 'Sinh')
@signature(BNum)
def builtin_sinh(x):
	"""Hyperbolic sine function."""
	return BType.from_python(cmath.sinh(x.value)).simplify()

@BBuiltin('Csh', 'Cosh')
@signature(BNum)
def builtin_cosh(x):
	"""Hyperbolic cosine function."""
	return BType.from_python(cmath.cosh(x.value)).simplify()

@BBuiltin('Tnh', 'Tanh')
@signature(BNum)
def builtin_tanh(x):
	"""Hyperbolic tangent function."""
	return BType.from_python(cmath.tanh(x.value)).simplify()

@BBuiltin('Ash', 'Asinh')
@signature(BNum)
def builtin_asinh(x):
	"""Hyperbolic arc sine function."""
	return BType.from_python(cmath.asinh(x.value)).simplify()

@BBuiltin('Ach', 'Acosh')
@signature(BNum)
def builtin_acosh(x):
	"""Hyperbolic arc cosine function."""
	return BType.from_python(cmath.acosh(x.value)).simplify()

@BBuiltin('Ath', 'Atanh')
@signature(BNum)
def builtin_atanh(x):
	"""Hyperbolic arc tangent function."""
	return BType.from_python(cmath.atanh(x.value)).simplify()


#################### Statistical functions ####################

@BBuiltin('Mn', 'Mean', 'Avg', 'Average')
@signature(BSeq)
def builtin_mean(s):
	"""Mean (average) value in a sequence."""
	sv = [x.value for x in s.simplify().value]
	return BComplex(sum(sv) / len(sv)).simplify()

@BBuiltin('Mi', 'Median')
@signature(BSeq)
def builtin_median(s):
	"""Median value in a sequence."""
	sv = [x.value for x in s.simplify().value]
	h = (len(sv) - 1) // 2
	e = (not len(sv) % 2) + 1
	return BComplex(sum(sorted(sv)[h:h+e]) / e).simplify()

@BBuiltin('Ml', 'Medianlow')
@signature(BSeq)
def builtin_median_low(s):
	"""Low median value in a sequence."""
	sv = [x.value for x in s.simplify().value]
	h = (len(sv) - 1) // 2
	e = (not len(sv) % 2) + 1
	return BComplex(sorted(sv)[h]).simplify()

@BBuiltin('Mh', 'Medianhigh')
@signature(BSeq)
def builtin_median_high(s):
	"""High median value in a sequence."""
	sv = [x.value for x in s.simplify().value]
	h = (len(sv) - 1) // 2
	e = (not len(sv) % 2) + 1
	return BComplex(sorted(sv)[h+e-1]).simplify()

@BBuiltin('Vr', 'Var', 'Variance')
@signature(BSeq)
def builtin_variance(s):
	"""Sample variance of a sequence."""
	sv = [x.value for x in s.simplify().value]
	n = len(sv)
	m = sum(sv) / n
	v = sum((m-x)**2 for x in sv) / (n - 1)
	return BComplex(v).simplify()

@BBuiltin('Vd', 'Stdev', 'Stdeviation')
@signature(BSeq)
def builtin_stdev(s):
	"""Sample standard deviation of a sequence."""
	sv = [x.value for x in s.simplify().value]
	n = len(sv)
	m = sum(sv) / n
	d = math.sqrt(sum((m-x)**2 for x in sv) / (n - 1))
	return BComplex(d).simplify()

@BBuiltin('Vp', 'Pvar', 'Popvariance')
@signature(BSeq)
def builtin_pop_variance(s):
	"""Population variance of a sequence."""
	sv = [x.value for x in s.simplify().value]
	n = len(sv)
	m = sum(sv) / n
	v = sum((m-x)**2 for x in sv) / n
	return BComplex(v).simplify()

@BBuiltin('Vs', 'Pstdev', 'Popstdeviation')
@signature(BSeq)
def builtin_pop_stdev(s):
	"""Population standard deviation of a sequence."""
	sv = [x.value for x in s.simplify().value]
	n = len(sv)
	m = sum(sv) / n
	d = math.sqrt(sum((m-x)**2 for x in sv) / n)
	return BComplex(d).simplify()

@BBuiltin('Mo', 'Mode')
@signature(BSeq)
def builtin_mode(s):
	"""Mode of a sequence."""
	sv = s.simplify().value
	c = collections.Counter(sv)
	return c.most_common(1)[0][0]


#################### Mathematical constants ####################

BBuiltin('Inf', 'Infinity', '∞', value=BFloat(float('inf')),
	doc="""Infinity.""")
BBuiltin('Infj', 'Infinityj', '∞j',
	value=BComplex(complex(0, float('inf'))),
	doc="""Complex infinity.""")
BBuiltin('Nan', value=BFloat(float('nan')),
	doc="""Not a number.""")
BBuiltin('Nanj', value=BComplex(complex(0, float('nan'))),
	doc="""Not a (complex) number.""")
BBuiltin('Pi', 'Mπ', value=BFloat(math.pi),
	doc="""Pi (3.14...).""")
BBuiltin('Tau', 'Ta', 'Mτ', 'Twopi', 'Τ', value=BFloat(2*math.pi),
	doc="""Tau = 2*pi (6.28...).""")
BBuiltin('Eta', 'Mη', 'Halfpi', 'Η', value=BFloat(math.pi/2),
	doc="""Eta = pi/2 (1.57...).""")
BBuiltin('Eu', 'Euler', 'Me', '€', 'ℇ', value=BFloat(math.e),
	doc="""Euler's constant, e (2.718...).""")
BBuiltin('Phi', 'Φ', 'Mφ', value=BFloat((1+math.sqrt(5))/2),
	doc="""The golden ratio, phi (1.618...).""")

# Fractions
BBuiltin('¼', value=BFloat(.25), doc="""1/4 = 0.25.""")
BBuiltin('½', value=BFloat(.5), doc="""1/2 = 0.5.""")
BBuiltin('¾', value=BFloat(.75), doc="""3/4 = 0.75.""")
BBuiltin('⅓', value=BFloat(1/3.), doc="""1/3 = 0.3333....""")
BBuiltin('⅔', value=BFloat(2/3.), doc="""2/3 = 0.6666....""")
BBuiltin('⅕', value=BFloat(.2), doc="""1/5 = 0.2.""")
BBuiltin('⅖', value=BFloat(.4), doc="""2/5 = 0.4.""")
BBuiltin('⅗', value=BFloat(.6), doc="""3/5 = 0.6.""")
BBuiltin('⅘', value=BFloat(.8), doc="""4/5 = 0.8.""")
BBuiltin('⅙', value=BFloat(1/6.), doc="""1/6 = 0.1666....""")
BBuiltin('⅚', value=BFloat(5/6.), doc="""5/6 = 0.8333....""")
BBuiltin('⅛', value=BFloat(.125), doc="""1/8 = 0.125.""")
BBuiltin('⅜', value=BFloat(.375), doc="""3/8 = 0.375.""")
BBuiltin('⅝', value=BFloat(.625), doc="""5/8 = 0.625.""")
BBuiltin('⅞', value=BFloat(.875), doc="""7/8 = 0.875.""")

# Useful integers
BBuiltin('Eo', 'Eof', value=BInt(-1),
	doc="""-1 = end-of-file (EOF).""")
BBuiltin('Ps', value=BInt(32),
	doc="""32 = 2^5 = the first printable ASCII character (space)""")
BBuiltin('Pa', value=BInt(127),
	doc="""127 = 2^7 - 1 = one greater than the last printable ASCII character (~).""")
BBuiltin('Pv', value=BInt(128), doc="""128 = 2^7.""")
BBuiltin('Pb', value=BInt(255), doc="""255 = 2^8 - 1.""")
BBuiltin('Px', value=BInt(256), doc="""256 = 2^8.""")


#################### Linear algebra functions ####################

BBuiltin('Id', 'Identity', code=',,[0]*1+*/(;',
	doc="""Make an identity matrix of size N.""")

BBuiltin('*m', 'Matrixproduct', code='?#@nT*c{T\\*n|+n}|/',
	doc="""Product of two matrices.""")
BBuiltin('^m', 'Matrixpower', code=',{(:N\\,*\\*mN*}{;#,,[0]*1+*/(;}I',
	doc="""Raise a square matrix to a power.""")
BBuiltin('*h', '∘', 'Hadamard', 'Hadamardproduct', code='Z{T\\*n|}|',
	doc="""Hadamard product of two matrices.""")

BBuiltin('#v', 'Δ', 'Vectornorm', 'Vectormag', code='\\Sq|+n',
	doc="""Euclidean norm (L^2 norm) of a vector.""")
BBuiltin('#l', 'Lnorm', code=',?i{M}{{?^p}|+s1@/^p}I',
	doc="""L^P norm of a vector for a given P.""")
BBuiltin('*d', '•', 'Dot', 'Dotproduct', 'Inner', 'Innerproduct',
	code='{Ft~}|Z\\*n|+n',
	doc="""Dot product (inner product) of two vectors.""")
BBuiltin('*o', 'Outer', 'Outerproduct', '⊗', code=']l${Ft~}|1/$*m',
	doc="""Outer product of two vectors.""")

@BBuiltin('*x', 'Cross', 'Crossproduct', '×')
@signature(BSeq, BSeq)
def builtin_cross_product(a, b):
	"""Cross product of two length-3 vectors."""
	avv = [ax.value for ax in a.simplify().value]
	bvv = [bx.value for bx in b.simplify().value]
	if len(avv) != 3 or len(bvv) != 3:
		raise ValueError('cannot take cross product of non-3D vectors')
	cvv = [avv[1] * bvv[2] - avv[2] * bvv[1],
		avv[2] * bvv[0] - avv[0] * bvv[2],
		avv[0] * bvv[1] - avv[1] * bvv[0]]
	return BList([BComplex(cvx).simplify() for cvx in cvv])

@BBuiltin('|m', 'Matrixmap')
def builtin_matrix_map(self, context, looping=False):
	"""Map a function onto a matrix."""
	f = context.pop()
	m = context.pop()
	if isinstance(f, BList) and isinstance(m, BFunc):
		f, m = m, f
	if not isinstance(f, BFunc) or not isinstance(m, BList):
		raise BTypeError(self, (m, f))
	map_tok = BToken('name', '|')
	mmv = []
	for r in m.value:
		if not isinstance(r, BSeq):
			raise BTypeError(self, (m, f))
		context.push(r)
		context.push(f)
		context.execute_token(map_tok)
		rm = context.pop()
		mmv.append(rm)
	context.push(BList(mmv))


#################### List functions ####################

BBuiltin('Nil', 'Nul', 'Null', 'Void', 'Empty', 'Ø', '∅', value=BList(),
	doc="""An empty list.""")

@BBuiltin('[', '⟨')
def builtin_mark_list(self, context, looping=False):
	"""Mark place in the stack."""
	context.leftbs.append(len(context.stack))

@BBuiltin(']', '⟩')
def builtin_push_list(self, context, looping=False):
	"""
	Make a list formed from the marked place in the stack.
	If no place is marked, use the entire stack.
	"""
	i = context.leftbs.pop() if context.leftbs else 0
	lv = context.pop_till(i)
	context.push(BList(lv))

BBuiltin(']l', 'Solo', code='[,;]',
	doc="""Wrap the top of the stack in a list.""")
BBuiltin(']p', 'Duo', 'Pair', code='[,t;t]',
	doc="""Wrap the top two items of the stack in a list.""")
BBuiltin(']t', 'Trio', code='[,r;r]',
	doc="""Wrap the top three items of the stack in a list.""")
BBuiltin(']f', 'Quartet', code='[,f;f]',
	doc="""Wrap the top four items of the stack in a list.""")

BBuiltin('(p', 'Car', code='(;p',
	doc="""First item of a sequence.""")
BBuiltin('Cdr', code='(;',
	doc="""Remove the first item of a sequence.""")
BBuiltin(')p', 'Carlast', code=');p',
	doc="""Last item of a sequence.""")

BBuiltin('(a', 'Cons', code=']l$+',
	doc="""Prepend a value to a sequence.""")
BBuiltin(')a', 'Rcons', code=']l+',
	doc="""Append a value to a sequence.""")

BBuiltin('Ui', 'Uptoinc', code=')U(;',
	doc="""List the integers in the interval [1, N].""")
BBuiltin('Uf', 'Upfrom', code='?_+U{?+}|;p',
	doc="""List the integers in the half-open interval [M, N).""")
BBuiltin('Uc', 'Upfrominc', code=')Uf',
	doc="""List the integers in the closed interval [M, N].""")
BBuiltin('Uo', 'Upfromex', code='$)$Uf',
	doc="""List the integers in the open interval (M, N).""")

@BBuiltin('#n', 'Count')
@signature(BSeq, _)
def builtin_count(s, e):
	"""Count the occurrences of a value in a sequence."""
	if isinstance(s, BList):
		return BInt(s.value.count(e))
	elif isinstance(s, BStr):
		return BInt(s.value.count(e.convert(BStr()).value))
	elif isinstance(s, BRegex):
		return BInt(s.value.pattern.count(e.convert(BStr()).value))

BBuiltin('K', 'In', 'Contains', '∈', '∋', code='#n0>',
	doc="""Test whether a sequence contains a value.""")
BBuiltin('Kn', 'Nin', 'Lacks', '∉', '∌', code='K!',
	doc="""Test whether a sequence does not contain a value.""")

@BBuiltin('F', 'Find', 'Indexof', 'Detect')
def builtin_find(self, context, looping=False):
	"""
	Index of a value in a sequence, or -1 if it is missing.
	Take the first item in a sequence that satisfies a predicate function,
	or Nan if no value satisfies it.
	"""
	v = context.pop()
	s = context.pop()
	if isinstance(v, BSeq) and not isinstance(s, BSeq):
		s, v = v, s
	if not isinstance(s, BSeq):
		raise BTypeError(self, (s, v))
	if isinstance(v, BFunc):
		sv = s.simplify().value
		for x in sv:
			context.push(x)
			v.apply(context)
			if context.pop():
				f = x
				break
		else:
			f = BFloat(float('nan'))
	elif isinstance(s, BList):
		try:
			f = BInt(s.value.index(v))
		except ValueError:
			f = BInt(-1)
	elif isinstance(s, BStr):
		try:
			vv = v.convert(BStr()).value
			f = BInt(s.value.index(vv))
		except ValueError:
			f = BInt(-1)
	elif isinstance(s, BStr):
		try:
			vv = v.convert(BStr()).value
			f = BInt(s.value.pattern.index(vv))
		except ValueError:
			f = BInt(-1)
	context.push(f)

@BBuiltin('Fs', 'Findsub')
@signature(BSeq, BSeq)
def builtin_count(s, v):
	"""Index of a subsequence in a sequence, or -1 if it is missing."""
	if isinstance(s, BList):
		sv = s.value
		vv = v.simplify().value
		vn = len(vv)
		for i in range(len(sv)-vn+1):
			for j in range(vn):
				if sv[i+j] != vv[j]:
					break
			else:
				return BInt(i)
		return BInt(-1)
	elif isinstance(s, BStr):
		try:
			vv = v.convert(BStr()).value
			return BInt(s.value.index(vv))
		except ValueError:
			return BInt(-1)
	elif isinstance(s, BStr):
		try:
			vv = v.convert(BStr()).value
			return BInt(s.value.pattern.index(vv))
		except ValueError:
			return BInt(-1)

@BBuiltin('Rm', 'Remove')
@signature(BSeq, _)
def builtin_remove(s, e):
	"""Remove the first occurrence of a value from a sequence."""
	if isinstance(s, BList):
		sv = s.value
		try:
			sv.remove(e)
		except ValueError:
			pass
		return s
	elif isinstance(s, BStr):
		ev = e.convert(BStr()).value
		return BStr(s.value.replace(ev, '', 1))
	elif isinstance(s, BRegex):
		ev = e.convert(BStr()).value
		pattern = s.value.pattern.replace(ev, '', 1)
		return BRegex(regex.compile(pattern, s.value.flags))

@BBuiltin('Rr', 'Rrm', 'Rremove')
@signature(BSeq, _)
def builtin_rremove(s, e):
	"""Remove the last occurrence of a value from a sequence."""
	if isinstance(s, BList):
		sv = s.value[::-1]
		try:
			sv.remove(e)
		except ValueError:
			pass
		return BList(sv[::-1])
	elif isinstance(s, BStr):
		ev = e.convert(BStr()).value
		return BStr(''.join(s.value.rsplit(ev, 1)))
	elif isinstance(s, BRegex):
		ev = e.convert(BStr()).value
		pattern = ''.join(s.value.pattern.rsplit(ev, 1))
		return BRegex(regex.compile(pattern, s.value.flags))

BBuiltin('Rma', 'Removeall', code='{,tK}{?pRm$}W;',
	doc="""Remove all occurrences of a value from a sequence.""")

BBuiltin('Rs', 'Rms', 'Removesub', code='\\Rm-',
	doc="""Remove the first occurrence of each item in a sequence from another sequence.""")
BBuiltin('Rsa', 'Rmsa', 'Removeallsub', 'Complement', '¢', '∁', code='\\Rma-',
	doc="""Remove all occurrences of each item in a sequence from another sequence.""")

@BBuiltin('Rp', 'Replace')
@signature(BSeq, _, _)
def builtin_replace(s, a, b):
	"""Replace all occurrences of one value in a sequence with another."""
	if a == b:
		return s
	if isinstance(s, BList):
		sv = s.value
		try:
			while True:
				sv[sv.index(a)] = b
		except ValueError:
			pass
		return s
	elif isinstance(s, BStr):
		sv = s.value
		av = a.convert(BStr()).value
		bv = b.convert(BStr()).value
		return BStr(sv.replace(av, bv))
	elif isinstance(s, BRegex):
		sv = s.value.pattern
		av = a.convert(BStr()).value
		bv = b.convert(BStr()).value
		pattern = sv.replace(av, bv)
		return BRegex(regex.compile(pattern, s.value.flags))

@BBuiltin('V', 'Ravel', 'Flatten')
@signature(_)
def builtin_ravel(a):
	"""Flatten a value into a list of scalar values."""
	def flatten(v):
		if isinstance(v, BList):
			return list(sum(map(flatten, v.value), []))
		elif isinstance(v, BSeq):
			return v.convert(BList()).value
		elif not isinstance(v, BSeq):
			return [v]
	return BList(flatten(a))

@BBuiltin('@s', 'Rotate')
@signature(BSeq, BInt)
def builtin_rotate(s, n):
	"""Rotate a sequence left by a number of items."""
	if isinstance(s, BRegex):
		sv, nv = s.value.pattern, n.value
		nv %= len(sv) if sv else 1
		return BRegex(regex.compile(sv[nv:] + sv[:nv], s.value.flags))
	else:
		sv, nv = s.value, n.value
		nv %= len(sv) if sv else 1
		return type(s)(sv[nv:] + sv[:nv])

@BBuiltin('&r', 'Reject')
def builtin_reject(self, context, looping=False):
	"""Filter a sequence by a negated predicate function."""
	b = context.pop()
	a = context.pop()
	if isinstance(a, BSeq) and isinstance(b, BFunc):
		a, b = b, a
	if not isinstance(a, BFunc) or not isinstance(b, BSeq):
		raise BTypeError(self, (a, b))
	cv = []
	bv = b.simplify().value
	for x in bv:
		context.push(x)
		a.apply(context)
		if not context.pop():
			cv.append(x)
	context.push(BList(cv).convert(b))

BBuiltin('*p', 'Intersperse', '⁂', code=']l*',
	doc="""Intersperse a value between the items of a sequence.""")

BBuiltin('&z', 'Compress', code='Z\\)p&\\(p|',
	doc="""Filter a sequence by the items' correspondence with true items in
another sequence.""")

BBuiltin('-v', 'Eachv', code='\\_$+-',
	doc="""Execute a function with each argument list in a sequence.""")
BBuiltin('/v', '⁄v', 'Partitionv', code='\\_$+/',
	doc="""Partition a sequence of argument lists with a predicate function.""")
BBuiltin('&v', 'Filterv', 'Selectv', '∩v', code='\\_$+&',
	doc="""Filter a sequence of argument lists by a predicate function.""")
BBuiltin('|v', 'Mapv', 'Collectv', '¦v', code='\\_$+|',
	doc="""Map a function onto a sequence of argument lists to the function.""")
BBuiltin('^v', 'Filterindexesv', code='\\_$+^',
	doc="""Filter a sequence of argument lists by a predicate function and take the indices.""")

@BBuiltin('&s', 'At', 'All', 'Every', '∀')
@signature(BSeq)
def builtin_all(s):
	"""Test whether all the values in a sequence are true."""
	return BInt(all(x for x in s.simplify().value))

@BBuiltin('|s', 'Et', 'Any', 'Some', '∃')
@signature(BSeq)
def builtin_any(s):
	"""Test whether any of the values in a sequence are true."""
	return BInt(any(x for x in s.simplify().value))

@BBuiltin('Af', 'None', 'Nany', '∃n', code='Et!')
@signature(BSeq)
def builtin_none(s):
	"""Test whether all the values in a sequence are false."""
	return BInt(all(not x for x in s.simplify().value))

@BBuiltin('Ef', 'Nall', '∀n', code='At!')
@signature(BSeq)
def builtin_any_not(s):
	"""Test whether any of the values in a sequence are true."""
	return BInt(any(not x for x in s.simplify().value))

BBuiltin('+s', 'Σ', '∑', 'Sum', code='\\+*',
	doc="""Fold a sequence with addition (i.e. find its sum).""")
BBuiltin('+n', '∫', 'Σn', '∑n', code='[0]$++s',
	doc="""Fold a sequence with addition, using 0 as the empty sum.""")
BBuiltin('+l', 'Σl', '∑l', code='[[]]$++s',
	doc="""Fold a sequence with addition, using [] as the empty sum.""")
BBuiltin('*s', 'Π', '∏', 'Product', code='\\**',
	doc="""Fold a sequence with multiplication (i.e. find its product).""")
BBuiltin('*n', 'Πn', '∏n', code='[1]$+*s',
	doc="""Fold a sequence with multiplication, using 1 as the empty product.""")

BBuiltin('-s', 'Differences', code='([][]p]$+{,@_@n-+]p}*_;p',
	doc="""Take successive differences of a sequence.""")
BBuiltin('/s', 'Ratios', code='([][]p]$+{,@_@n/+]p}*_;p',
	doc="""Take successive ratios of a sequence.""")

BBuiltin('Sn', 'Natsort', 'Naturalsort', code='{`(\\d+)`~l{,?d{,X$#_}It}|}S',
	doc="""Sort a sequence of strings in a natural order.""")

@BBuiltin('#h', 'Shape')
@signature(_)
def builtin_shape(a):
	"""Shape of a sequence."""
	if not isinstance(a, BSeq):
		# Shape of a scalar
		return BList()
	elif isinstance(a, BList):
		# Shape of a list
		bv = []
		s = a
		while isinstance(s, BSeq):
			if isinstance(s, BList):
				bv.append(BInt(len(s.value)))
				s = s.value[0] if s.value else None
			elif isinstance(s, BStr):
				bv.append(BInt(len(s.value)))
				s = None
			elif isinstance(s, BRegex):
				bv.append(BInt(len(s.value.pattern)))
				s = None
		return BList(bv)
	elif isinstance(a, BStr):
		# Shape of string
		return BList([BInt(len(a.value))])
	elif isinstance(a, BRegex):
		# Shape of regex
		return BList([BInt(len(a.value.pattern))])

@BBuiltin('Ch', 'Choices')
@signature(BSeq, BNum)
def builtin_choices(s, n):
	"""List all combinations of N items from a sequence."""
	sv = s.simplify().value
	nv = n.simplify().value
	cv = [BList(c).convert(s) for c in itertools.combinations(sv, nv)]
	return BList(cv)

@BBuiltin('Chr', 'Repchoices')
@signature(BSeq, BNum)
def builtin_rep_choices(s, n):
	"""List all combinations with replacement of N items from a sequence."""
	sv = s.simplify().value
	nv = n.simplify().value
	cv = [BList(c).convert(s) for c in
		itertools.combinations_with_replacement(sv, nv)]
	return BList(cv)

@BBuiltin('Zt', 'Zipthree')
@signature(BSeq, BSeq, BSeq)
def builtin_zip_three(a, b, c):
	"""Zip three sequences together."""
	s = min([a, b, c], key=lambda x: x.rank)
	av = a.simplify().value
	bv = b.simplify().value
	cv = c.simplify().value
	zv = [BList(zx).convert(s) for zx in zip(av, bv, cv)]
	return BList(zv)

@BBuiltin('Zf', 'Zipfour')
@signature(BSeq, BSeq, BSeq, BSeq)
def builtin_zip_four(a, b, c, d):
	"""Zip four sequences together."""
	s = min([a, b, c, d], key=lambda x: x.rank)
	av = a.simplify().value
	bv = b.simplify().value
	cv = c.simplify().value
	dv = d.simplify().value
	zv = [BList(zx).convert(s) for zx in zip(av, bv, cv, dv)]
	return BList(zv)

@BBuiltin('Zv', 'Zipfive')
@signature(BSeq, BSeq, BSeq, BSeq, BSeq)
def builtin_zip_five(a, b, c, d, e):
	"""Zip five sequences together."""
	s = min([a, b, c, d, e], key=lambda x: x.rank)
	av = a.simplify().value
	bv = b.simplify().value
	cv = c.simplify().value
	dv = d.simplify().value
	ev = d.simplify().value
	zv = [BList(zx).convert(s) for zx in zip(av, bv, cv, dv, ev)]
	return BList(zv)

@BBuiltin('Zx', 'Zipsix')
@signature(BSeq, BSeq, BSeq, BSeq, BSeq, BSeq)
def builtin_zip_six(a, b, c, d, e, f):
	"""Zip six sequences together."""
	s = min([a, b, c, d, e, f], key=lambda x: x.rank)
	av = a.simplify().value
	bv = b.simplify().value
	cv = c.simplify().value
	dv = d.simplify().value
	ev = d.simplify().value
	fv = d.simplify().value
	zv = [BList(zx).convert(s) for zx in zip(av, bv, cv, dv, ev, fv)]
	return BList(zv)

@BBuiltin('*c', '*cartesian', 'Cartesianproduct')
@signature(BSeq, BSeq)
def builtin_cartesian_product(a, b):
	"""Cartesian product of two sequences."""
	s = min([a, b], key=lambda x: x.rank)
	av = a.simplify().value
	bv = b.simplify().value
	return BList([BList([x, y]).convert(s) for x in av for y in bv])

BBuiltin('Subset', '⊆', '⊂', code='-!',
	doc="""Test whether a sequence is a subset of another sequence.""")
BBuiltin('Psubset', '⊊', code=',t=!@nSubset?I',
	doc="""Test whether a sequence is a proper subset of another sequence.""")
BBuiltin('Superset', '⊇', '⊃', code='$Subset',
	doc="""Test whether a sequence is a superset of another sequence.""")
BBuiltin('Psuperset', '⊋', code='$Psubset',
	doc="""Test whether a sequence is a proper superset of another sequence.""")


#################### Array functions ####################

@BBuiltin(']g', 'Get')
@signature(BSeq, BInt)
def builtin_get(s, i):
	"""Get the item in a sequence at an index."""
	return s.simplify().value[i.value]

@BBuiltin(']s', 'Set')
def builtin_set(self, context, looping=False):
	"""Set the item in a sequence at an index to a value."""
	v = context.pop()
	i = context.pop()
	s = context.pop()
	if isinstance(s, BInt) and isinstance(i, BSeq):
		s, i = i, s
	if not isinstance(s, BSeq) or not isinstance(i, BInt):
		raise BTypeError(self, (s, i))
	x = s.simplify()
	x.value[i.value] = v
	context.push(x.convert(s))

@BBuiltin('[s', 'Setr')
def builtin_setr(self, context, looping=False):
	"""Set a value as the item in a sequence at an index."""
	s = context.pop()
	i = context.pop()
	v = context.pop()
	if isinstance(s, BInt) and isinstance(i, BSeq):
		s, i = i, s
	if not isinstance(s, BSeq) or not isinstance(i, BInt):
		raise BTypeError(self, (s, i))
	x = s.simplify()
	x.value[i.value] = v
	context.push(x.convert(s))

@BBuiltin(']d', 'Del')
@signature(BSeq, BInt)
def builtin_del(s, i):
	"""Delete the item in a sequence at an index."""
	x = s.simplify()
	x.value = x.value[:i.value] + x.value[i.value+1:]
	return x.convert(s)

@BBuiltin('Ss', 'Slice')
def builtin_slice(self, context, looping=False):
	"""
	Slice a sequence given start, stop, and/or step parameters.
	One parameter is treated as the stop value; two as start and stop
	values; three as start, stop, and step values. Parameters may be
	separate integers or grouped in a list.
	"""
	a = context.pop()
	if isinstance(a, BSeq):
		b = context.pop()
		if not isinstance(b, BSeq):
			raise BTypeError(self, a)
		s = b
		sv = b.convert(BList()).value
		av = a.convert(BList()).value
		if not all(isinstance(x, BInt) for x in av):
			raise BTypeError(self, (b, a))
		avv = [x.value for x in av]
		if len(avv) == 1:
			stop = avv[0]
			start = step = None
		else:
			avv.extend([None, None, None])
			start, stop, step = avv[:3]
	elif isinstance(a, BInt):
		b = context.pop()
		if isinstance(b, BSeq):
			s = b
			sv = b.convert(BList()).value
			stop = a.value
			start = step = None
		elif isinstance(b, BInt):
			c = context.pop()
			if isinstance(c, BSeq):
				s = c
				sv = c.convert(BList()).value
				start = b.value
				stop = a.value
				step = None
			elif isinstance(c, BInt):
				d = context.pop()
				if isinstance(d, BSeq):
					s = d
					sv = d.convert(BList()).value
					start = c.value
					stop = b.value
					step = a.value
				else:
					raise BTypeError(self, (d, c, b, a))
			else:
				raise BTypeError(self, (c, b, a))
		else:
			raise BTypeError(self, (b, a))
	else:
		raise BTypeError(self, a)
	context.push(BList(sv[start:stop:step]).convert(s))


#################### Associative array functions ####################

@BBuiltin('#k', 'Haskey', 'Containskey')
@signature(BList, _)
def builtin_haskey(s, k):
	"""Test whether a key exists in a list of [key value] pairs."""
	for p in s.value:
		if isinstance(p, BList) and p.value[0] == k:
			return BInt(1)
	return BInt(0)

@BBuiltin('#g', 'Getvalue', 'Lookup')
@signature(BList, _)
def builtin_getvalue(s, k):
	"""
	Get the value associated with a key in a list of [key value] pairs,
	or Nan if the key does not exist."""
	for p in s.value:
		if isinstance(p, BList) and p.value[0] == k:
			return p.value[1]
	return BFloat(float('nan'))

@BBuiltin('#s', 'Setkey', 'Setvalue', 'Store')
@signature(BList, _, _)
def builtin_setvalue(s, k, v):
	"""Set the value associated with a key in a list of [key value] pairs."""
	for p in s.value:
		if p.value[0] == k:
			p.value[1] = v
			return s
	s.value.append(BList([k, v]))
	return s

@BBuiltin('#d', 'Delkey', 'Deletekey')
@signature(BList, _)
def builtin_delkey(s, k):
	"""Delete a key from a list of [key value] pairs."""
	return BList([p for p in s.value if p.value[0] != k])


#################### Control flow functions ####################

@BBuiltin('I', 'If')
def builtin_if(self, context, looping=False):
	"""If 'cond' is true, apply 'then'; otherwise apply 'else'."""
	do_else = context.pop()
	do_then = context.pop()
	if context.pop():
		do_then.apply(context)
	else:
		do_else.apply(context)

BBuiltin('Iu', 'Unless', code='$I',
	doc="""If 'cond' is false, apply 'then'; otherwise apply 'else'.""")
BBuiltin('It', 'Then', code='{}I',
	doc="""If 'cond' is true, apply 'then'.""")
BBuiltin('Ie', 'Else', code='{}$I',
	doc="""If 'cond' is false, apply 'then'.""")

@BBuiltin('D', 'Do', 'Dowhile')
def builtin_do_while(self, context, looping=False):
	"""Apply 'body'. While popped is true, apply 'body'."""
	do_body = context.pop()
	if not isinstance(do_body, BFunc):
		raise BTypeError(self, do_body)
	do_body.apply(context, looping=True)
	cond = context.pop()
	while cond and not context.broken:
		do_body.apply(context, looping=True)
		cond = context.pop()
	if context.broken != BContext.EXITED:
		context.broken = False

@BBuiltin('Du', 'Dountil')
def builtin_do_until(self, context, looping=False):
	"""Apply 'body'. While popped is false, apply 'body'."""
	do_body = context.pop()
	if not isinstance(do_body, BFunc):
		raise BTypeError(self, do_body)
	do_body.apply(context, looping=True)
	cond = context.pop()
	while not cond.value and not context.broken:
		do_body.apply(context, looping=True)
		cond = context.pop()
	if context.broken != BContext.EXITED:
		context.broken = False

@BBuiltin('W', 'While')
def builtin_while(self, context, looping=False):
	"""Apply 'cond'. While popped is true, apply 'body' and 'cond'."""
	do_body = context.pop()
	do_cond = context.pop()
	if not isinstance(do_body, BFunc):
		raise BTypeError(self, (do_cond, do_body))
	do_cond.apply(context)
	cond = context.pop()
	while cond and not context.broken:
		do_body.apply(context, looping=True)
		do_cond.apply(context)
		cond = context.pop()
	if context.broken != BContext.EXITED:
		context.broken = False

BBuiltin('Wt', 'Whiletrue', 'Forever', code='1$W',
	doc="""Repeatedly apply a function forever.""")

@BBuiltin('Bk', 'Break', '↯')
def builtin_break(self, context, looping=False):
	"""Break out of a number of loops."""
	a = context.pop()
	if not isinstance(a, BNum):
		raise BTypeError(self, a)
	av = int(a.simplify().value)
	ctx = context
	while av > 0 and ctx:
		ctx.broken = True
		if ctx.looping:
			ctx.looping = False
			av -= 1
		ctx = ctx.parent
	if ctx:
		ctx.broken = True

BBuiltin('Br', '↵', code='1Bk', doc="""Break out of the current loop.""")

@BBuiltin('Ex', 'Exit', '∎')
def builtin_break(self, context, looping=False):
	"""Exit the script."""
	ctx = context
	while ctx:
		ctx.broken = BContext.EXITED
		ctx.looping = False
		ctx = ctx.parent

@BBuiltin('Rt', 'Ret', 'Return', '↩', '↪')
def builtin_return(self, context, looping=False):
	"""Return from a function."""
	ctx = context
	while ctx and not ctx.scoped:
		ctx.broken = True
		ctx = ctx.parent
	while ctx and ctx.script is not BBlock.NONLOCAL:
		ctx.broken = True
		ctx = ctx.parent
	if ctx:
		ctx.broken = True

@BBuiltin('Ll', 'Label')
def builtin_label(self, context, looping=False):
	"""The program counter."""
	main = context
	while main.parent:
		main = main.parent
	context.push(BInt(main.counter + 1))

@BBuiltin('Go', 'Goto')
def builtin_goto(self, context, looping=False):
	"""Set the program counter to a number."""
	a = context.pop()
	if not isinstance(a, BNum):
		raise BTypeError(self, a)
	av = int(a.simplify().value)
	context.counter = av - 1

BBuiltin('Cnt', 'Cont', 'Continue', '↺', '↻', code='0Go',
	doc="""Continue execution from the start of a function.""")


#################### String functions ####################

@BBuiltin('"', 'List', 'String', 'Tokens')
@signature(_)
def builtin_sequence(a):
	"""
	Convert a string or regex to a list.
	Convert a list or number to a string.
	Convert a function to a list of tokens.
	"""
	if isinstance(a, BChars):
		return a.convert(BList())
	elif isinstance(a, BFunc):
		return BList([BStr(str(t)) for t in a.simplify().value])
	return a.convert(BStr())

BBuiltin('.', 'Endl', value=BStr('\n'),
	doc="""A string with a single newline.""")

BBuiltin('Dg', 'Digits', code='58U48>"', value=BStr('0123456789'),
	doc="""The ten ASCII digits.""")
BBuiltin('Au', 'Alphaupper', code='95U65>"',
	value=BStr('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
	doc="""The 26 ASCII uppercase letters.""")
BBuiltin('Al', 'Alphalower', code='123U97>"',
	value=BStr('abcdefghijklmnopqrstuvwxyz'),
	doc="""The 26 ASCII lowercase letters.""")
BBuiltin('Aa', 'Alphabet', code='AuAl+',
	value=BStr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'),
	doc="""The 52 ASCII uppercase and lowercase letters.""")

@BBuiltin('%f', 'Fmt', 'Format')
@signature(BSeq, _)
def builtin_format(f, v):
	"""Format a string by a value."""
	fv = f.convert(BStr()).value
	return BStr(fv % v.format_value())

@BBuiltin('Y', 'Tr', 'Translate', 'Transliterate', '¥')
@signature(BSeq, (BInt, BSeq), (BInt, BSeq))
def builtin_translate(s, t, r):
	"""
	Replace items in a sequence found in a search sequence with their
	corresponding items in a replacement sequence. Items not in the search
	sequence are unchanged. Items in the search sequence without
	corresponding ones in the replacement sequence are deleted.
	"""
	sv = s.convert(BList()).value
	tv = t.convert(BList()).value
	rv = r.convert(BList()).value
	table = {c: None for c in tv}
	table.update(dict(zip(tv, rv)))
	yv = [y for y in [table.get(x, x) for x in sv] if y is not None]
	return BList(yv).convert(s)

@BBuiltin('Yd', 'Trd', 'Translateordelete')
@signature(BSeq, (BInt, BSeq), (BInt, BSeq))
def builtin_translate_or_delete(s, t, r):
	"""
	Replace items in a sequence found in a search sequence with their
	corresponding items in a replacement sequence. Items not in the search
	sequence, and items in the search sequence without corresponding ones
	in the replacement sequence, are deleted.
	"""
	sv = s.convert(BList()).value
	tv = t.convert(BList()).value
	rv = r.convert(BList()).value
	table = dict(zip(tv, rv))
	yv = [y for y in [table.get(x, None) for x in sv] if y is not None]
	return BList(yv).convert(s)

@BBuiltin('Xb', 'Birdieescape')
@signature(BSeq)
def bultin_birdiescript_escape(s):
	"""Escape a Birdiescript string."""
	return BStr(escape_birdiescript(s.convert(BStr()).value))

@BBuiltin('Xr', 'Regexescape')
@signature(BSeq)
def bultin_regex_escape(s):
	"""Escape a regular expression string."""
	return BStr(re.escape(s.convert(BStr()).value))

@BBuiltin('?d', 'Isdigit')
@signature((BInt, BSeq))
def builtin_isdigit(s):
	"""Test whether a string is numeric."""
	sv = s.convert(BStr()).value
	return BInt(sv.isdigit())

@BBuiltin('?l', 'Isalpha')
@signature((BInt, BSeq))
def builtin_isalpha(s):
	"""Test whether a string is alphabetical."""
	sv = s.convert(BStr()).value
	return BInt(sv.isalpha())

@BBuiltin('?w', 'Isalnum')
@signature((BInt, BSeq))
def builtin_isalnum(s):
	"""Test whether a string is alphanumeric."""
	sv = s.convert(BStr()).value
	return BInt(sv.isalnum())

@BBuiltin('?s', 'Isspace')
@signature((BInt, BSeq))
def builtin_isspace(s):
	"""Test whether a string is whitespace."""
	sv = s.convert(BStr()).value
	return BInt(sv.isspace())

@BBuiltin('?a', 'Isprintable')
@signature((BInt, BSeq))
def builtin_isprintable(s):
	"""Test whether a string is printable ASCII."""
	sv = s.convert(BStr()).value
	return BInt(all(32 <= ord(c) <= 126 for c in sv))

@BBuiltin('Cu', 'Upper', 'Uppercase')
@signature((BInt, BSeq))
def builtin_uppercase(s):
	"""Convert a string to uppercase."""
	sv = s.convert(BStr()).value
	return BStr(sv.upper())

@BBuiltin('Cw', 'Lower', 'Lowercase')
@signature((BInt, BSeq))
def builtin_lowercase(s):
	"""Convert a string to lowercase."""
	sv = s.convert(BStr()).value
	return BStr(sv.lower())

@BBuiltin('Ct', 'Title', 'Titlecase')
@signature((BInt, BSeq))
def builtin_titlecase(s):
	"""Convert a string to title case."""
	sv = s.convert(BStr()).value
	return BStr(sv.title())

@BBuiltin('Cs', 'Swapcase')
@signature((BInt, BSeq))
def builtin_swapcase(s):
	"""Swap the case of a string."""
	sv = s.convert(BStr()).value
	return BStr(sv.swapcase())

@BBuiltin('^s', 'Starts')
@signature(BSeq, (BInt, BSeq))
def builtin_starts(s, w):
	"""Test if a string starts with a given substring."""
	sv, wv = s.convert(BStr()).value, w.convert(BStr()).value
	return BInt(sv.startswith(wv))

@BBuiltin('$s', 'Ends')
@signature(BSeq, (BInt, BSeq))
def builtin_ends(s, w):
	"""Test if a string ends with a given substring."""
	sv, wv = s.convert(BStr()).value, w.convert(BStr()).value
	return BInt(sv.endswith(wv))

@BBuiltin('St', 'Strip')
@signature(BSeq, (BInt, BSeq))
def builtin_strip(s, c):
	"""Strip the given characters from both ends of a string."""
	sv = s.convert(BStr()).value
	cv = c.convert(BStr()).value
	return BStr(sv.strip(cv))

@BBuiltin('Stw', 'Stripspace')
@signature(BSeq, (BInt, BSeq))
def builtin_strip_space(s, c):
	"""Strip whitespace from both ends of a string."""
	return BStr(s.convert(BStr()).value.strip())

@BBuiltin('Sl', 'Lstrip')
@signature(BSeq, (BInt, BSeq))
def builtin_lstrip(s, c):
	"""Strip the given characters from the beginning of a string."""
	sv = s.convert(BStr()).value
	cv = c.convert(BStr()).value
	return BStr(sv.lstrip(cv))

@BBuiltin('Slw', 'Lstripspace')
@signature(BSeq, (BInt, BSeq))
def builtin_lstrip_space(s, c):
	"""Strip whitespace from the beginning of a string."""
	return BStr(s.convert(BStr()).value.lstrip())

@BBuiltin('Sr', 'Rstrip')
@signature(BSeq, (BInt, BSeq))
def builtin_rstrip(s, c):
	"""Strip the given characters from the end of a string."""
	sv = s.convert(BStr()).value
	cv = c.convert(BStr()).value
	return BStr(sv.rstrip(cv))

@BBuiltin('Srw', 'Rstripspace')
@signature(BSeq, (BInt, BSeq))
def builtin_rstrip_space(s, c):
	"""Strip whitespace from the end of a string."""
	return BStr(s.convert(BStr()).value.rstrip())

@BBuiltin('J', 'Jr', 'Justify', 'Rjustify')
@signature(BSeq, BInt, (BInt, BSeq))
def builtin_rjustify(s, w, p):
	"""Right-justify a string to a given width with a given padding character."""
	sv = s.convert(BStr()).value
	pv = p.convert(BStr()).value
	return BStr(sv.rjust(w.value, pv))

BBuiltin('Jw', 'Jrw', code="' J",
	doc="""Right-justify a string to a given width with spaces.""")
BBuiltin('Jz', 'Jrz', code="'0J",
	doc="""Right-justify a string to a given width with zeros.""")
BBuiltin('Jo', 'Jro', code='0J',
	doc="""Right-justify a string to a given width with null characters.""")

@BBuiltin('Jl', 'Ljustify')
@signature(BSeq, BInt, (BInt, BSeq))
def builtin_ljustify(s, w, p):
	"""Left-justify a string to a given width with a given padding character."""
	sv = s.convert(BStr()).value
	pv = p.convert(BStr()).value
	return BStr(sv.ljust(w.value, pv))

BBuiltin('Jlw', code="' Jl",
	doc="""Left-justify a string to a given width with spaces.""")
BBuiltin('Jlz', code="'0Jl",
	doc="""Left-justify a string to a given width with zeros.""")
BBuiltin('Jlo', code='0Jl',
	doc="""Left-justify a string to a given width with null characters.""")

@BBuiltin('Jc', 'Center', 'Cjustify')
@signature(BSeq, BInt, (BInt, BSeq))
def builtin_center(s, w, p):
	"""Center a string to a given width with a given padding character."""
	sv = s.convert(BStr()).value
	pv = p.convert(BStr()).value
	return BStr(sv.center(w.value, pv))

BBuiltin('Jcw', code="' Jc",
	doc="""Center a string to a given width with spaces.""")
BBuiltin('Jcz', code="'0Jc",
	doc="""Center a string to a given width with zeros.""")
BBuiltin('Jco', code='0Jc',
	doc="""Center a string to a given width with null characters.""")

@BBuiltin('%w', 'Words', '§')
@signature(BSeq)
def builtin_words(s):
	"""Split a string at runs of whitespace, removing empty substrings."""
	sv = s.convert(BStr()).value
	return BList([BStr(w) for w in sv.split()])

@BBuiltin('*w', 'Unwords')
@signature(BSeq)
def builtin_unwords(s):
	"""Join a sequence of strings with spaces."""
	if not isinstance(s, BList):
		return s.convert(BStr())
	sv = [x.convert(BStr()).value for x in s.value]
	return BStr(' '.join(sv))

@BBuiltin('/l', 'Lines', '¶')
@signature(BSeq)
def builtin_lines(s):
	"""Split a string at newlines."""
	sv = s.convert(BStr()).value
	return BList([BStr(l) for l in sv.split('\n')])

@BBuiltin('*l', 'Unlines')
@signature(BSeq)
def builtin_unlines(s):
	"""Join a sequence of strings with newlines."""
	if not isinstance(s, BList):
		return s.convert(BStr())
	sv = [x.convert(BStr()).value for x in s.value]
	return BStr('\n'.join(sv))


#################### Regular expression functions ####################

@BBuiltin('~f', 'Findall')
@signature(BSeq, BSeq)
def builtin_findall(s, rx):
	"""
	Find all non-overlapping matches of a regular expression in a string.
	Expressions without capture groups match as strings. Expressions with
	capture groups match as lists of captured strings.
	"""
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	fvv = regex.findall(rxv, sv)
	fv = []
	for xv in fvv:
		if isinstance(xv, tuple):
			x = BList([BStr(yv) for yv in xv])
		else:
			x = BStr(xv)
		fv.append(x)
	return BList(fv)

@BBuiltin('~m', 'Match')
@signature(BSeq, BSeq)
def builtin_match(s, rx):
	"""
	Match a regular expression with the beginning of a string, or 0
	if there is no match.
	Expressions without capture groups match as a string. Expressions with
	capture groups match as a list of captured strings.
	"""
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	m = regex.match(rxv, sv)
	if not m:
		return BInt(0)
	if not m.groups():
		return BStr(m.group(0))
	return BList([BStr(xv) for xv in m.groups()])

@BBuiltin('~s', 'Search')
@signature(BSeq, BSeq)
def builtin_search(s, rx):
	"""
	Find the first match of a regular expression in a string, or 0
	if there is no match.
	Expressions without capture groups match as a string. Expressions with
	capture groups match as a list of captured strings.
	"""
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	m = regex.search(rxv, sv)
	if not m:
		return BInt(0)
	if not m.groups():
		return BStr(m.group(0))
	return BList([BStr(xv) for xv in m.groups()])

@BBuiltin('~p', 'Span', 'Searchspan')
@signature(BSeq, BSeq)
def builtin_search_span(s, rx):
	"""
	Find the first match of a regular expression in a string and get its
	spanning indices, or 0 if there is no match.
	"""
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	m = regex.search(rxv, sv)
	if not m:
		return BInt(0)
	return BList([BInt(xv) for xv in m.span()])

@BBuiltin('~g', 'Gsub', 'Gsubstitute')
def builtin_gsub(self, context, looping=False):
	"""
	Replace all non-overlapping matches of a regular expression in a string
	with a replacement value. If the value is a function, it is applied to
	each match to yield the replacement value; otherwise, it is used as a
	replacement string itself.
	"""
	p = context.pop()
	rx = context.pop()
	s = context.pop()
	if not areinstances((s, rx), BSeq):
		raise BTypeError(self, (s, rx, p))
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	if isinstance(p, BFunc):
		def pf(m):
			if not m.groups():
				h = BStr(m.group(0))
			else:
				h = BList([BStr(xv) for xv in m.groups()])
			context.push(h)
			p.apply(context)
			r = context.pop()
			return r.convert(BStr()).value
		gv = regex.sub(rxv, pf, sv)
		context.push(BStr(gv).convert(s))
	else:
		pv = p.convert(BStr()).value
		gv = regex.sub(rxv, pv, sv)
		context.push(BStr(gv).convert(s))

@BBuiltin('~l', 'Gsplit')
@signature(BSeq, BSeq)
def builtin_gsplit(s, rx):
	"""Split a string at each match of a regular expression."""
	sv = s.convert(BStr()).value
	rxv = rx.convert(BRegex()).value
	lvv = regex.split(rxv, sv)
	return BList([BStr(xv) for xv in lvv])


#################### Input functions ####################

@BBuiltin('>e', 'Getenc', 'Getencoding')
def builtin_encoding(self, context, looping=False):
	"""The character encoding for input sources."""
	context.push(BStr(context.encoding))

@BBuiltin('<e', 'Setenc', 'Setencoding')
def builtin_encoding(self, context, looping=False):
	"""Set the character encoding for input sources."""
	e = context.pop()
	if not isinstance(e, BSeq):
		raise BTypeError(self, e)
	context.encoding = e.convert(BStr()).value

@BBuiltin('%g', 'Getenv')
@signature(BSeq)
def builtin_getenv(n):
	"""Get an environment variable by name."""
	nv = n.convert(BStr()).value
	vv = os.environ.get(nv, None)
	if vv is not None:
		return BStr(vv)
	return BInt(0)

@BBuiltin('>i', 'Read', '◊')
@signature()
def builtin_read():
	"""Read up to EOF from standard input."""
	return BStr(sys.stdin.read())

@BBuiltin('>c', 'Readchar')
@signature()
def builtin_readchar():
	"""Read a single character from standard input."""
	rv = sys.stdin.read(1)
	if not rv:
		return BInt(-1)
	return BStr(rv).simplify().value[0]

@BBuiltin('>n', 'Readline')
@signature()
def builtin_readline():
	"""Read up to a newline from standard input."""
	return BStr(sys.stdin.readline())

@BBuiltin('>o', 'Readstring')
@signature()
def builtin_readstring():
	"""Read up to a null character from standard input."""
	rv = []
	while True:
		c = sys.stdin.read(1)
		if not c or c == '\0':
			break
		rv.append(c)
	return BStr(''.join(rv))

@BBuiltin('>w', 'Readword')
@signature()
def builtin_readtoken():
	"""Read up to a whitespace character from standard input."""
	rv = []
	while True:
		c = sys.stdin.read(1)
		if not c or c.isspace():
			break
		rv.append(c)
	return BStr(''.join(rv))

@BBuiltin('>t', 'Readupto')
@signature((BInt, BSeq))
def builtin_readupto(t):
	"""Read up to a given character or characters from standard input."""
	if t == BInt(-1):
		return BStr(sys.stdin.read())
	tv = set(t.convert(BStr()).value)
	rv = []
	while True:
		c = sys.stdin.read(1)
		if not c or c in tv:
			break
		rv.append(c)
	return BStr(''.join(rv))

@BBuiltin('>f', 'Readfile')
def builtin_readfile(self, context, looping=False):
	"""
	Read the contents of a file with a given name.
	If an error occurs, return its error code, or -1.
	"""
	f = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, f)
	filename = f.convert(BStr()).value
	try:
		with codecs.open(filename, 'rU', context.encoding) as file:
			rv = file.read()
		c = BStr(rv)
	except EnvironmentError as ex:
		c = BInt(ex.errno)
	except Exception:
		c = BInt(-1)
	context.push(c)

@BBuiltin('>b', 'Readbinary')
def builtin_readbinary(self, context, looping=False):
	"""
	Read the contents of a binary file with a given name.
	If an error occurs, return its error code, or -1.
	"""
	f = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, f)
	filename = f.convert(BStr()).value
	try:
		with codecs.open(filename, 'rb', context.encoding) as file:
			rv = file.read()
		c = BList([BInt(ord(b)) for b in rv])
	except EnvironmentError as ex:
		c = BInt(ex.errno)
	except Exception:
		c = BInt(-1)
	context.push(c)

@BBuiltin('>u', 'Readurl')
def builtin_readurl(self, context, looping=False):
	"""
	Read the contents of a network resource with a given URL.
	If an error occurs, return its HTTP status code, or -1.
	"""
	u = context.pop()
	if not isinstance(u, BSeq):
		raise BTypeError(self, u)
	url = u.convert(BStr()).value
	try:
		handle = urllib.urlopen(url)
		rv = handle.read()
		handle.close()
		c = BStr(rv.decode(context.encoding))
	except EnvironmentError as ex:
		c = BInt(ex.errno)
	except Exception:
		c = BInt(-1)
	context.push(c)

@BBuiltin('>x', 'System', '⌘')
@signature(BSeq)
def builtin_system(c):
	"""
	Execute a sequence as a system command and get the output or error code.
	"""
	cmd = c.convert(BStr()).value
	argv = shlex.split(cmd)
	try:
		rv = subprocess.check_output(argv)
		return BStr(rv)
	except subprocess.CalledProcessError as ex:
		return BInt(-ex.returncode)
	except EnvironmentError as ex:
		return BInt(ex.errno)
	except Exception:
		return BInt(-1)


#################### Output functions ####################

@BBuiltin('O', 'Out')
def builtin_out(self, context, looping=False):
	"""Print a value."""
	a = context.top()
	print(safe_string(a), end='')

BBuiltin('P', 'Print', code='O;',
	doc="""Pop and print a value.""")
BBuiltin('.p', 'Pendl', code='.P',
	doc="""Print a single newline.""")
BBuiltin('Of', 'Outf', code='%fO',
	doc="""Format a string by a value and print it.""")
BBuiltin('On', 'Outln', code='O.p',
	doc="""Print a value followed by a newline.""")
BBuiltin('Ofn', 'Outfln', code='%fOn',
	doc="""Format a string by a value and print it followed by a newline.""")
BBuiltin('Pf', 'Printf', code='Of;',
	doc="""Format a string by a value, pop it, and print it.""")
BBuiltin('Pn', 'Println', code='On;',
	doc="""Pop and print a value followed by a newline.""")
BBuiltin('Pfn', 'Printfln', code='Ofn;',
	doc="""Format a string by a value, pop it, and print it followed by a newline.""")

@BBuiltin('%s', 'Setenv')
@signature(BSeq, _)
def builtin_setenv(n, v):
	"""Set the named environment variable to a given value."""
	nv = n.convert(BStr()).value
	if isinstance(v, BNum):
		vv = str(v)
	else:
		vv = v.convert(BStr()).value
	os.environ[nv] = vv

@BBuiltin('%u', 'Unsetenv')
@signature(BSeq)
def builtin_setenv(n):
	"""Unset an environment variable by name."""
	nv = n.convert(BStr()).value
	del os.environ[nv]

@BBuiltin('<f', 'Writefile')
def builtin_writefile(self, context, looping=False):
	"""Write a value to the a file with a given name."""
	f = context.pop()
	c = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, (f, c))
	filename = f.convert(BStr()).value
	content = c.convert(BStr()).value
	try:
		with codecs.open(filename, 'wU', context.encoding) as file:
			file.write(content)
	except Exception:
		pass

@BBuiltin('<b', 'Writebinary')
def builtin_writebinary(self, context, looping=False):
	"""Write a binary value to the a file with a given name."""
	f = context.pop()
	c = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, (f, c))
	filename = f.convert(BStr()).value
	content = bytearray(c.convert(BList()).value)
	try:
		with codecs.open(filename, 'wb', context.encoding) as file:
			file.write(content)
	except Exception:
		pass

@BBuiltin('<a', 'Appendfile')
def builtin_appendfile(self, context, looping=False):
	"""Append a value to the a file with a given name."""
	f = context.pop()
	c = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, (f, c))
	filename = f.convert(BStr()).value
	content = c.convert(BStr()).value
	try:
		with codecs.open(filename, 'aU', context.encoding) as file:
			file.write(content)
	except Exception:
		pass

@BBuiltin('<c', 'Appendbinary')
def builtin_appendbinary(self, context, looping=False):
	"""Append a binary value to the a file with a given name."""
	f = context.pop()
	c = context.pop()
	if not isinstance(f, BSeq):
		raise BTypeError(self, (f, c))
	filename = f.convert(BStr()).value
	content = bytearray(c.convert(BList()).value)
	try:
		with codecs.open(filename, 'ab', context.encoding) as file:
			file.write(content)
	except Exception:
		pass


#################### Meta functions ####################

@BBuiltin('Ty', 'Type')
@signature(_)
def builtin_type(a):
	"""
	The type ID of a value.
	0 = integer
	1 = float
	2 = complex
	3 = list
	4 = string
	5 = regex
	6 = block
	7 = builtin
	"""
	return BInt(a.rank)

@BBuiltin(']b', 'Block')
@signature(_)
def builtin_block(a):
	"""Wrap a value in a block."""
	return BBlock(a.tokenize())

@BBuiltin('G', 'Show')
@signature(_)
def builtin_show(a):
	"""Convert a value to a string, as it would appear if printed."""
	return BStr(str(a))

@BBuiltin('R', 'Repr', '⌜', '⌝')
@signature(_)
def builtin_repr(a):
	"""Convert a value to its Birdiescript representation."""
	return BStr(repr(a))

@BBuiltin('X', 'Exec', 'Eval', 'Execute', 'Evaluate', 'Apply', '⌥')
def builtin_eval(self, context, looping=False):
	"""
	Evaluate a sequence as a Birdiescript string.
	Execute a function.
	"""
	a = context.pop()
	if isinstance(a, BSeq):
		# Evaluate sequence as Birdiescript string
		ab = a.convert(BStr()).convert(BBlock())
		ab.apply(context)
	else:
		# Execute a function
		a.apply(context)

@BBuiltin('Xp', 'Execpy', 'Python')
def builtin_exec_python(self, context, looping=False):
	"""
	Execute a sequence as Python code.
	
	The Birdiescript stack is made available in the _ variable, with
	Birdiescript types converted to their native Python equivalents.
	After execution, the stack is converted back to Birdiescript.
	
	A local Python namespace is reused throughout the current context, and
	a global namespace is reused throughout the whole script. This allows
	consecutive Execpy calls to share data without passing it along the
	Birdiescript stack.
	
	For example, the code:
	    `x=2` Xp `_.append(x)` Xp
	will push 2 onto the Birdiescript stack.
	
	In the code:
	    {`x=1;global y;y=2` Xp} X `_.append(y)` Xp
	the variable y is still accessible outside the Birdiescript block,
	since it is declared global.
	"""
	a = context.pop()
	ab = a.convert(BStr())
	py_code = ab.value
	context.local_py_ns['_'] = [x.python_value() for x in context.stack]
	exec_python(py_code, context.global_py_ns, context.local_py_ns)
	py_stack = context.local_py_ns.get('_', [])
	stack = [BType.from_python(v) for v in py_stack]
	context.replace_stack(stack)

BBuiltin('Xf', 'Execfile', code='>fX',
	doc="""Evaluate the contents of a file with a given name as a
Birdiescript string.""")


#################### Pseudorandomness functions ####################

@BBuiltin('Rd', 'Seed')
def builtin_seed(self, context, looping=False):
	"""
	Seed the random number generator with an integer, or with the
	current time if not an integer.
	"""
	a = context.top()
	if isinstance(a, BInt):
		context.pop()
		random.seed(a.value)
	else:
		random.seed()

@BBuiltin('Ra', 'Rand', 'Random')
@signature()
def builtin_rand():
	"""Choose a random variate uniformly in the interval [0, 1)."""
	return BFloat(random.random())

@BBuiltin('Rn', 'Randnorm', 'Randomnormal', 'Randgauss', 'Randomgaussian')
@signature(BReal, BReal)
def builtin_random_normal(mu, sigma):
	"""
	Choose a random variate from a normal (Gaussian) distribution,
	given the parameters mu and sigma.
	"""
	return BFloat(random.gauss(mu.value, sigma.value))

@BBuiltin('Rl', 'Randlognorm', 'Randomlognormal')
@signature(BReal, BReal)
def builtin_random_log_normal(mu, sigma):
	"""
	Choose a random variate from a log-normal distribution,
	given the parameters mu and sigma.
	"""
	return BFloat(random.lognormvariate(mu.value, sigma.value))

@BBuiltin('Rf', 'Randuni', 'Randomuniform')
@signature(BReal, BReal)
def builtin_random_uniform(a, b):
	"""Choose a random variate uniformly in the interval [A, B)."""
	return BFloat(random.uniform(a.value, b.value))

@BBuiltin('Rb', 'Randbeta', 'Randombeta')
@signature(BReal, BReal)
def builtin_random_beta(alpha, beta):
	"""
	Choose a random variate from a beta distribution,
	given the parameters alpha > 0 and beta > 0.
	"""
	return BFloat(random.betavariate(alpha.value, beta.value))

@BBuiltin('Ru', 'Randtri', 'Randomtriangluar')
@signature(BReal, BReal, BReal)
def builtin_random_triangular(low, high, mode):
	"""
	Choose a random variate from a triangular distribution,
	given the lower limit, upper limit, and mode.
	"""
	return BFloat(random.triangular(low.value, high.value, mode.value))

@BBuiltin('Rg', 'Randgamma', 'Randomgamma')
@signature(BReal, BReal)
def builtin_random_gamma(alpha, beta):
	"""
	Choose a random variate from a gamma distribution,
	given the parameters alpha and beta.
	"""
	return BFloat(random.gammavariate(alpha.value, beta.value))

@BBuiltin('Ro', 'Randpareto', 'Randompareto')
@signature(BReal, BReal)
def builtin_random_pareto(alpha):
	"""
	Choose a random variate from a Pareto distribution,
	given the parameter alpha.
	"""
	return BFloat(random.paretovariate(alpha.value))

@BBuiltin('Rx', 'Randexp', 'Randomexponential')
@signature(BReal, BReal)
def builtin_random_exponential(lambd):
	"""
	Choose a random variate from an exponential distribution,
	given the parameter lambda.
	"""
	return BFloat(random.expovariate(lambd.value))

@BBuiltin('Rw', 'Randweibull', 'Randomweibull')
@signature(BReal, BReal)
def builtin_random_weibull(alpha, beta):
	"""
	Choose a random variate from a Weibull distribution,
	given the parameters alpha and beta.
	"""
	return BFloat(random.weibullvariate(alpha.value, beta.value))

@BBuiltin('Rv', 'Randvm', 'Randomvonmises')
@signature(BReal, BReal)
def builtin_random_von_mises(mu, kappa):
	"""
	Choose a random variate from a von Mises distribution,
	given the parameters mu and kappa.
	"""
	return BFloat(random.vonmisesvariate(mu.value, kappa.value))


#################### Time functions ####################

@BBuiltin('Sp', 'Slp', 'Sleep')
@signature(BReal)
def builtin_sleep(n):
	"""Delay execution for a number of seconds."""
	time.sleep(n.value)

@BBuiltin('Ck', 'Clock')
@signature()
def builtin_clock():
	"""
	CPU time (on Unix) or wall-clock time elapsed since the first call
	to Clock (on Windows).
	"""
	return BFloat(time.clock())

@BBuiltin('Tu', 'Gmttime', 'Utctime')
@signature((BReal, BList))
def builtin_utctime(t):
	"""
	Convert an epoch time to a [yr mon day hr min sec wd yd dst] list
	structure in UTC/GMT, or vice-versa.
	"""
	if isinstance(t, BReal):
		tv = [BInt(xv) for xv in time.gmtime(t.value)]
		return BList(tv)
	elif isinstance(t, BList):
		tvv = [x.value for x in t.value]
		return BInt(calendar.timegm(tvv))

@BBuiltin('Tl', 'Localtime')
@signature((BReal, BList))
def builtin_localtime(t):
	"""
	Convert an epoch time to a [yr mon day hr min sec wd yd dst] list
	structure in the local timezone, or vice-versa.
	"""
	if isinstance(t, BReal):
		tv = [BInt(xv) for xv in time.localtime(t.value)]
		return BList(tv)
	elif isinstance(t, BList):
		tvv = [x.value for x in t.value]
		return BInt(time.mktime(tvv))

@BBuiltin('Tf', 'Formattime')
@signature(BSeq, (BReal, BSeq))
def builtin_formattime(f, t):
	"""
	Format an epoch time or a time structure according to a format string,
	or parse a string into an time structure according to a format string.
	Epoch times are assumed to be in UTC/GMT.
	"""
	fv = f.convert(BStr()).value
	if isinstance(t, BReal):
		tv = time.gmtime(t.value)
		return BStr(time.strftime(fv, tv))
	elif isinstance(t, BList):
		tv = [x.value for x in t.value]
		return BStr(time.strftime(fv, tv))
	elif isinstance(t, BChars):
		tv = t.convert(BStr()).value
		sv = [BInt(xv) for xv in time.strptime(fv, tv)]
		return BList(sv)

@BBuiltin('Tc', 'Ctime')
@signature((BReal, BSeq))
def builtin_ctime(t):
	"""
	Convert an epoch time or a time structure to a string formatted as
	`%a %b %d %H:%M:%S %Y`, or parse such a string into a time structure.
	"""
	if isinstance(t, BReal):
		return BStr(time.ctime(t.value))
	elif isinstance(t, BList):
		tvv = [x.value for x in t.value]
		return BStr(time.asctime(tvv))
	elif isinstance(t, BChars):
		tv = t.convert(BStr()).value
		svv = datetime.datetime.strptime(tv, '%a %b %d %H:%M:%S %Y')
		return BList([BInt(xv) for xv in svv])

@BBuiltin('Ti', 'Isotime')
@signature((BReal, BSeq))
def builtin_isotime(t):
	"""
	Convert an epoch time or a time structure to a string formatted as
	`%Y-%m-%dT%H:%M:%S`, or parse such a string into a time structure.
	"""
	iso_fmt = '%Y-%m-%dT%H:%M:%S'
	if isinstance(t, BReal):
		return BStr(time.strftime(iso_fmt, time.localtime(t.value)))
	elif isinstance(t, BList):
		tvv = [x.value for x in t.value]
		return BStr(time.strftime(iso_fmt, tvv))
	elif isinstance(t, BChars):
		tv = t.convert(BStr()).value
		svv = datetime.datetime.strptime(tv, iso_fmt)
		return BList([BInt(xv) for xv in svv])

@BBuiltin('Td', 'Date')
@signature((BReal, BList))
def builtin_date(t):
	"""Convert an epoch time or a time structure to a [yr mon day] list."""
	if isinstance(t, BReal):
		tv = [BInt(xv) for xv in time.localtime(t.value)[:3]]
		return BList(tv)
	elif isinstance(t, BList):
		return BList(t.value[:3])

@BBuiltin('Tt', 'Time')
@signature((BReal, BList))
def builtin_time(t):
	"""Convert an epoch time or a time structure to a [hr min sec] list."""
	if isinstance(t, BReal):
		tv = [BInt(xv) for xv in time.localtime(t.value)[3:6]]
		return BList(tv)
	elif isinstance(t, BList):
		return BList(t.value[3:6])

@BBuiltin('Tn', 'Now')
@signature()
def builtin_now():
	"""Current time in seconds since the epoch (1970-01-01T00:00:00Z)."""
	return BFloat(time.time())

BBuiltin('Tnu', 'Nowutc', code='TnTu',
	doc="""Current time as a list structure in UTC/GMT.""")
BBuiltin('Tnl', 'Nowlocal', code='TnTl',
	doc="""Current time as a list structure in the local timezone.""")
BBuiltin('Tnf', 'Formatnow', code='TnTf',
	doc="""Format the current time according to a format string.""")
BBuiltin('Tnd', 'Nowdate', code='TnTd',
	doc="""Current date as a [yr mon day] list.""")
BBuiltin('Tnt', 'Nowtime', code='TnTt',
	doc="""Current time as a [hr min sec] list.""")
BBuiltin('Tnc', 'Nowctime', code='TnTc',
	doc="""Current time formatted as `%a %b %d %H:%M:%S %Y`.""")
BBuiltin('Tni', 'Nowisotime', code='TnTi',
	doc="""Current time formatted as `%Y-%m-%dT%H:%M:%S`.""")

BBuiltin('Tz', 'Timezone', value=BInt(time.timezone),
	doc="""Offset of the local non-DST timezone in seconds west of UTC.""")
BBuiltin('Tzn', 'Tzname', 'Timezonename', value=BStr(time.tzname[0]),
	doc="""Name of the local non-DST timezone.""")

BBuiltin('Tdn', 'Days', value=BList([BStr(dv) for dv in calendar.day_name]),
	doc="""Names of the days of the week in the current locale.""")
BBuiltin('Tda', 'Dayabbrs', value=BList([BStr(dv) for dv in calendar.day_abbr]),
	doc="""Abbreviations of the days of the week in the current locale.""")
BBuiltin('Tmn', 'Months', value=BList([BStr(dv) for dv in calendar.month_name]),
	doc="""Names of the months of the year in the current locale.""")
BBuiltin('Tma', 'Monthabbrs', value=BList([BStr(dv) for dv in calendar.month_abbr]),
	doc="""Abbreviations of the months of the year in the current locale.""")


#################### Miscellaneous functions ####################

BBuiltin('Cel', 'Celsius', 'Fahrtocel', '℃', code='32-1.8/',
	doc="""Convert degrees Fahrenheit to degrees Celsius.""")
BBuiltin('Fahr', 'Fahrenheit', 'Celtofahr', '℉', code='1.8*32+',
	doc="""Convert degrees Celsius to degrees Fahrenheit.""")

@BBuiltin('Csr', 'Caesar', 'Cæ', code='26%2*AuAlZ",@{(+}*$Y')
@signature(BSeq, BInt)
def builtin_caesar_cipher(s, n):
	"""Caesar cipher: shift the letters in a string left by a number."""
	plain = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	sv = s.convert(BStr()).value
	nv = n.value % len(plain)
	cipher = plain[-nv:] + plain[:-nv]
	plain += plain.lower()
	cipher += cipher.lower()
	table = dict(zip(plain, cipher))
	cv = ''.join(table.get(c, c) for c in sv)
	return BStr(cv)

BBuiltin('Rtt', 'Rotthirteen', code='13Csr', altcode='Aa13/1@s,~"$"Y',
	doc="""ROT-13 cipher: shift the letters in a string by 13 places.""")


#################### REPL functions ####################

@BBuiltin('Ostack', 'Outstack')
def builtin_out_stack(self, context, looping=False):
	"""Print each item on the stack, separated by newlines."""
	print_tok = BToken('name', 'P')
	nl_tok = BToken('name', '.')
	imax = len(context.stack) - 1
	stack = context.stack[:]
	for (i, x) in enumerate(stack):
		context.push(x)
		context.execute_token(print_tok)
		if i < imax:
			context.execute_token(nl_tok)
			context.execute_token(print_tok)

BBuiltin('Pstack', 'Printstack', code='Ostack;',
	doc="""Pop and print each item on the stack, separated by newlines.""")

@BBuiltin('Odoc', 'Outdoc')
def builtin_print_doc(self, context, looping=False):
	"""Print the documentation for a value."""
	a = context.top()
	if isinstance(a, BBuiltin):
		usage = 'Names: ' + ' '.join(a.value)
		doc = a.apply.__doc__
	else:
		usage = 'Value: ' + str(a).replace('\n', ' ').strip()
		doc = a.__class__.__doc__
	doc = doc or '(None)'
	lines = [d.lstrip('\t').rstrip() for d in doc.split('\n') if d]
	desc = '\n'.join([usage] + lines).strip()
	print(desc, end='')
	nl_tok = BToken('name', '.')
	context.execute_token(nl_tok)
	print(context.pop(), end='')

BBuiltin('Pdoc', 'Printdoc', code='Odoc;',
	doc="""Pop a value and print its documentation.""")

@BBuiltin('Olocals', 'Outlocals', 'Plocals', 'Printlocals')
def builtin_print_locals(self, context, looping=False):
	"""Print the definitions local to the current scope."""
	nl_tok = BToken('name', '.')
	for (name, value) in sorted(context.scope.items(), key=lambda x: x[0]):
		value = '{}: {}'.format(name, repr(value))
		print(value, end='')
		context.execute_token(nl_tok)
		print(context.pop(), end='')

@BBuiltin('Ovars', 'Outvars', 'Pvars', 'Printvars')
def builtin_print_vars(self, context, looping=False):
	"""Print the definitions visible in the current scope."""
	contexts = []
	ctx = context
	while ctx:
		contexts.append(ctx)
		ctx = ctx.parent
	scopes = {}
	while contexts:
		ctx = contexts.pop()
		scopes.update(ctx.scope)
	nl_tok = BToken('name', '.')
	for (name, value) in sorted(scopes.items(), key=lambda x: x[0]):
		value = '{}: {}'.format(name, repr(value))
		print(value, end='')
		context.execute_token(nl_tok)
		print(context.pop(), end='')

@BBuiltin('Pbuiltins', 'Printbuiltins')
def builtin_print_builtins(self, context, looping=False):
	"""Print the definitions of the built-in functions."""
	nl_tok = BToken('name', '.')
	for name in sorted(builtins.keys()):
		print(name, end='')
		context.execute_token(nl_tok)
		print(context.pop(), end='')
