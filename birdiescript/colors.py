# -*- coding: utf-8 -*-
"""
Platform-independent console colors.
"""

from __future__ import (absolute_import, division, generators, nested_scopes,
	print_function, unicode_literals, with_statement)

import sys
import ctypes

if sys.platform == 'win32':
	# color_console.py
	# Copyright (C) Andre Burgaud
	# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
	
	_SHORT = ctypes.c_short
	_WORD = ctypes.c_ushort
	
	class _COORD(ctypes.Structure):
		"""struct in wincon.h."""
		_fields_ = [
			('X', _SHORT),
			('Y', _SHORT)]
	
	class _SMALL_RECT(ctypes.Structure):
		"""struct in wincon.h."""
		_fields_ = [
			('Left', _SHORT),
			('Top', _SHORT),
			('Right', _SHORT),
			('Bottom', _SHORT)]
	
	class _CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
		"""struct in wincon.h."""
		_fields_ = [
			('dwSize', _COORD),
			('dwCursorPosition', _COORD),
			('wAttributes', _WORD),
			('srWindow', _SMALL_RECT),
			('dwMaximumWindowSize', _COORD)]
	
	# winbase.h
	_STD_INPUT_HANDLE  = -10
	_STD_OUTPUT_HANDLE = -11
	_STD_ERROR_HANDLE  = -12
	
	# wincon.h
	FG_BLACK   = 0x0000
	FG_BLUE    = 0x0001
	FG_GREEN   = 0x0002
	FG_CYAN    = 0x0003
	FG_RED     = 0x0004
	FG_MAGENTA = 0x0005
	FG_YELLOW  = 0x0006
	FG_GREY    = 0x0007
	FG_BOLD    = 0x0008
	FG_NOBOLD  = 0x0000
	
	BG_BLACK   = 0x0000
	BG_BLUE    = 0x0010
	BG_GREEN   = 0x0020
	BG_CYAN    = 0x0030
	BG_RED     = 0x0040
	BG_MAGENTA = 0x0050
	BG_YELLOW  = 0x0060
	BG_GREY    = 0x0070
	BG_BOLD    = 0x0080
	BG_NOBOLD  = 0x0000
	
	_STDOUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(_STD_OUTPUT_HANDLE)
	
	_SetConsoleTextAttribute = ctypes.windll.kernel32.SetConsoleTextAttribute
	_GetConsoleScreenBufferInfo = ctypes.windll.kernel32.GetConsoleScreenBufferInfo
	
	def _get_text_attrs():
		csbi = _CONSOLE_SCREEN_BUFFER_INFO()
		_GetConsoleScreenBufferInfo(_STDOUT_HANDLE, ctypes.byref(csbi))
		return csbi.wAttributes
	
	def set_colors(attrs):
		_SetConsoleTextAttribute(_STDOUT_HANDLE, attrs)
	
	def raw_colors_string(attrs):
		_SetConsoleTextAttribute(_STDOUT_HANDLE, attrs)
		return ''
	
	DEFAULT_COLORS = _get_text_attrs()
else:
	class _AnsiCode(str):
		def __or__(self, other):
			return _AnsiCode(self + ';' + other)
	
	FG_BLACK   = _AnsiCode('30')
	FG_RED     = _AnsiCode('31')
	FG_GREEN   = _AnsiCode('32')
	FG_YELLOW  = _AnsiCode('33')
	FG_BLUE    = _AnsiCode('34')
	FG_MAGENTA = _AnsiCode('35')
	FG_CYAN    = _AnsiCode('36')
	FG_GREY    = _AnsiCode('37')
	FG_RESET   = _AnsiCode('39')
	FG_BOLD    = _AnsiCode('1')
	FG_NOBOLD  = _AnsiCode('22')
	
	BG_RED     = _AnsiCode('41')
	BG_GREEN   = _AnsiCode('42')
	BG_BLACK   = _AnsiCode('40')
	BG_YELLOW  = _AnsiCode('43')
	BG_BLUE    = _AnsiCode('44')
	BG_MAGENTA = _AnsiCode('45')
	BG_CYAN    = _AnsiCode('46')
	BG_GREY    = _AnsiCode('47')
	BG_RESET   = _AnsiCode('49')
	BG_BOLD    = _AnsiCode('1')
	BG_NOBOLD  = _AnsiCode('22')
	
	def set_colors(attrs):
		sys.stdout.write('\x1b[' + attrs + 'm')
	
	def raw_colors_string(attrs):
		return '\x1b[' + attrs + 'm'
	
	DEFAULT_COLORS = _AnsiCode('0')
