#!usr/bin/python
#
# (C) Legoktm, 2009 MIT License 
#
__version__ = '$Id$'
"""
Tags pages for RFD
Usage: python rfd.py
"""
import re

from pywikibot import wiki
o = wiki.Page('User:Arthur Rubin/Roman redirects')
list = re.findall('\[\[:M(.*?)\]\]', o.get())
newlist = []
for i in list:
	newlist.append(wiki.Page('M' + i))
append='{{rfd}}\n'
summary='Tagging for [[WP:RFD]] per [[WP:BOTR#Roman_redirects|request]]'
for b in newlist:
	oldtext = b.get(force=True)
	if 'rfd' in oldtext:
		print 'Skipping: ' + b.title()
		pass
	else:
		wiki.showDiff(oldtext, append+oldtext)
		b.put(append+oldtext, summary)