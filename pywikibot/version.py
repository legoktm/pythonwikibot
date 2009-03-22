#!usr/bin/python
#-*- coding: utf-8 -*-
__version__ = '$Id$'
import sys, re
try:
	import wiki
except:
	wiki = False
def getversion():
    return 'r%(rev)s, %(ts)s' % getversiondict()
def getversiondict():
		if wiki:
			id = wiki.__version__
		else:
			wikifile = open('wiki.py','r')
			text = wikifile.read()
			wikifile.close()
			Re = re.compile("\$Id: wiki\.py (.*?) \$")
			id = Re.findall(text)[0]
		dict = {
			'rev':id.split(' ')[2],
			'date':id.split(' ')[3],
			'ts':id.split(' ')[4],
			'user':id.split(' ')[5],
		}
		return dict
getversion()

if __name__ == '__main__':
	print 'PythonWikiBot: '+ getversion()
	print 'Python: '+sys.version