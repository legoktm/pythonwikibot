#!usr/bin/python
#
# (C) Legoktm 2009
# Released under the MIT License
#
# All pages should be in the wiki.Page() format
__version__ = '$Id$'

import wiki, config, catlib
import sys, re

def category(page, recurse=False):
	return catlib.Category(page, recurse=recurse)
def transclude(page):
	"""
	Returns pages that transclude a certain template
	"""
	API = wiki.API(wiki=page.getSite())
	print 'Getting references to [[%s]]...' %(page.title())
	params = {
		'action':'query',
		'list':'embeddedin',
		'eititle':page.title(),
		'eilimit':'max',
	}
	res = API.query(params)
	for page in res['query']['embeddedin']:
		yield wiki.Page(page['title'])

def prefixindex(page):
	"""
	Returns list of pages with prefix of the page ([[Special:PrefixIndex]])
	"""
	API = wiki.API(wiki=page.getSite())
	ns = page.namespace()
	prefix = page.titlewonamespace()
	params = {
		'action':'query',
		'list':'allpages',
		'apprefix':prefix,
		'apnamespace':str(ns),
		'aplimit':'max',
	}
	res = API.query(params)['query']['allpages']
	list = []
	for page in res:
		yield wiki.Page(page['title'])

def catlinks(page):
	print 'Getting categories on %s...' %str(page)
	gen = links(page, ns=14)
	for cat in gen:
		for page in category(cat):
			yield page

def recentchanges(limit = 500, nobot = True, onlyanon = False, hidepatrolled = True, nponly = False, wiki=config.wiki):
	"""
	Returns a list of articles that were recently changed ([[Special:RecentChanges]])
	If nponly = True, returns only newpages ([[Special:NewPages]])
	"""
	rcshow = []
	if nobot:
		rcshow.append('!bot')
	if onlyanon:
		rcshow.append('anon')
#	if hidepatrolled:
#		rcshow.append('!patrolled')
	rcshowparam = ''
	if len(rcshow) != 0:
		for i in rcshow:
			if i == rcshow[len(rcshow)-1]: #meaning it is the last one..
				rcshowparam += i
			else:
				rcshowparam += i + '|'
	params = {
		'action':'query',
		'list':'recentchanges',
		'rcshow':rcshowparam,
		'rcprop':'title',
		'rclimit':limit
	}
	if nponly:
		print 'Fetching the %s newest pages' %limit
		params['rctype'] = 'new'
	else:
		print 'Fetching the %s latest edits' %limit
	API = wiki.API(qcontinue=False, wiki=wiki)
	res = API.query(params)['query']['recentchanges']
	for page in res:
		yield wiki.Page(page['title'])

def links(page, ns=None):
	"""
	Returns links on a provided page
	Not Special:WhatLinksHere
	ns is an (optional) int() which is the only namespace returned
	"""
	API = wiki.API(wiki=page.getSite())
	params = {
		'action':'query',
		'titles':page.title(),
		'prop':'links',
		'pllimit':'max'
	}
	if ns:
		params['plnamespace'] = int(ns)
	res = API.query(params)['query']['pages']
	list = res[res.keys()[0]]['links']
	for page in list:
		yield wiki.Page(page['title'])

def whatlinkshere(page):
	"""
	[[Special:WhatLinksHere]]
	"""
	API = wiki.API(wiki=page.getSite())
	params = {
		'action':'query',
		'bltitle':page.title(),
		'list':'backlinks',
		'bllimit':'max',
	}
	res = API.query(params)['query']['backlinks']
	for i in res:
		yield wiki.Page(i['title'])
	
parameterHelp = """\
-cat              Work on all pages which are in a specific category.
                  Argument can also be given as "-cat:categoryname" or
                  as "-cat:categoryname|fromtitle".

-new              Work on the 60 newest pages. If given as -new:x, will work
                  on the x newest pages.

-file             Read a list of pages to treat from the named text file.
                  Page titles in the file must be enclosed with [[brackets]].
                  Argument can also be given as "-file:filename".

-links            Work on all pages that are linked from a certain page.
                  Argument can also be given as "-links:linkingpagetitle".

-catlinks        Work on all categories that are linked from a certain page.		
				 Argument can also be given as "-catlinks:linkingpagetitle".

-prefixindex      Work on pages commencing with a common prefix.
"""



def handleArgs():
	"""
	Picks the generator per argument passed in command line
	Usage:
	gen = pagegen.handleArgs()
	for page in gen:
	...do something
	"""
	for arg in wiki.getArgs():
		if arg.startswith('-catlinks'):
			if len(arg) == 9:
				pg = raw_input('Which page should be operated on? ')
				return catlinks(wiki.Page(pg))
			else: #means that page has been supplied
				pg = arg[10:]
				return catlinks(wiki.Page(pg))	
		if arg.startswith('-cat'):
			if len(arg) == 4:
				cat = raw_input('Which category should be operated on? ')
				if not 'category' in cat.lower():
					cat = 'Category:' + cat
				return category(wiki.Page(cat))
			else: #means that category has been supplied
				cat = arg[5:]
				if not 'category' in cat.lower():
					cat = 'Category:' + cat
				return category(wiki.Page(cat))
		if arg.startswith('-file'):
			if len(arg) == 5:
				fil = raw_input('Which file should be read? ')
			else: #means that file has been supplied
				fil = arg[6:]
			try:
				file = open(fil, 'r')
			except IOError, err:
				print err
				sys.exit(1)
			text = file.read()
			list = re.findall('\[\[(.*?)\]\]', text)
			newlist = []
			for i in list:
				newlist.append(wiki.Page(i))
			return newlist
		if arg.startswith('-new'):
			if len(arg) == 4:
				return recentchanges()
			else:
				try:
					limit = int(arg[5:])
				except:
					return recentchanges()
				return recentchanges(limit=limit)		
	#nothing found
	print parameterHelp
	sys.exit(1)
