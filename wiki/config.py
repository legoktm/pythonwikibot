#!usr/bin/python
__version__ = '$Id$'
import sys
try:
	import userconfig
except ImportError:
	sys.exit('Please run generate_config.py script to generate your preferences')
username = userconfig.username
quitonmess = userconfig.quitonmess
wiki = userconfig.wiki
commons = userconfig.commons
ts = userconfig.ts
maxlag = userconfig.maxlag
path = userconfig.path