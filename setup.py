#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

from distutils.core import setup
from distutils.command.install_scripts import install_scripts

def get_version():
	"""Get Birdiescript version without importing birdiescript.__init__."""
	path = os.path.join(os.path.dirname(__file__), 'birdiescript')
	f, pathname, desc = imp.find_module('__version__', [path])
	try:
		v = imp.load_module('__version__', f, pathname, desc)
		return v.version
	finally:
		f.close()

version = get_version()

long_description = '...'

script_name = 'birdiescript'

class birdie_install_scripts(install_scripts):
	""" Customized install_scripts."""
	
	def run(self):
		install_scripts.run(self)
		if sys.platform == 'win32':
			try:
				script_dir = os.path.join(sys.prefix, 'Scripts')
				script_path = os.path.join(script_dir, script_name)
				bat_str = '@"%s" "%s" %%*' % (sys.executable, script_path)
				bat_path = os.path.join(self.install_dir, '%s.bat' % script_name)
				f = open(bat_path, 'w')
				f.write(bat_str)
				f.close()
				print('Created: %s' % bat_path)
			except Exception:
				_, err, _ = sys.exc_info() # for both 2.x & 3.x compatability
				print('ERROR: Unable to create %s: %s' % (bat_path, err))

setup(
	name =          'Birdiescript',
	version =       version,
	url =           'http://www.remyoukaour.com/projects/birdiescript/',
	download_url =  'http://www.remyoukaour.com/projects/birdiescript/birdiescript-%s.zip' % version,
	description =   'Birdiescript reference implementation.',
	long_description = long_description,
	author =        'Remy Oukaour',
	author_email =  'remy [dot] oukaour [at] gmail [dot] com',
	maintainer =    'Remy Oukaour',
	maintainer_email = 'remy [dot] oukaour [at] gmail [dot] com',
	license =       'MIT/X11',
	packages =      ['birdiescript'],
	scripts =       ['bin/%s' % script_name],
	cmdclass =      {'install_scripts': birdie_install_scripts}
)
