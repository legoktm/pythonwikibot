#!usr/bin/python
#
# (C) Legoktm 2009
# Released under the MIT License
#
# All pages should be in the wiki.Page() format
__version__ = '$Id$'

import wiki, config
import sys, re
"""
Gets all articles in a certain category and returns a list
Recurse can be an integer or True for a full recurse
"""
class Category:
	def __init__(self, page, recurse = False):
		self.page = page
		self.site = self.page.site()
		if not self.page.isCategory():
			raise wiki.NotCategory(page.title())
		self.API = wiki.API(wiki=self.site)
		self.rinfinite = False #set it now, change it later
		if recurse:
			if type(recurse) is type(0):
				self.recurse = recurse
			elif type(recurse) is type(True): #has to be true
				self.recurse = recurse
				self.rinfinite = True
			elif type(recurse) is type(''):
				try:
					recurse = int(recurse)
					self.recurse = recurse
				except: #wtf??
					self.recurse = False
			else: #wtf??
				self.recurse = False
		
	def get(self):
		self.params = {
			'action':'query',
			'list':'categorymembers',
			'cmtitle':self.page.title(),
			'cmlimit':'max',
		}
		print 'Getting %s...' %self.page.aslink()
		res = self.API.query(self.params)['query']['categorymembers']
		list = []

def category(page):
	if not page.isCategory():
		raise wiki.NotCategory(page.title())
	API = wiki.API(wiki=page.site())
	print 'Getting %s...' %page.aslink()
	params = {
		'action':'query',
		'list':'categorymembers',
		'cmtitle':page.title(),
		'cmlimit':'max',
	}
	result = API.query(params)
	#format the list
	list = []
	res = result['query']['categorymembers']
	for page in res:
		try:
			list.append(wiki.Page(page['title']))
		except UnicodeEncodeError:
			pass
	return list
"""
Returns pages that transclude a certain template
"""
def transclude(page):
	API = wiki.API(wiki=page.site())
	print 'Getting references to [[%s]]...' %(page.title())
	params = {
		'action':'query',
		'list':'embeddedin',
		'eititle':page.title(),
		'eilimit':'max',
	}
	res = API.query(params)
	list = []
	for page in res['query']['embeddedin']:
		list.append(wiki.Page(page['title']))
	return list
"""
Returns list of pages with prefix of the page ([[Special:PrefixIndex]])
"""
def prefixindex(page):
	API = wiki.API(wiki=page.site())
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
		list.append(wiki.Page(page['title']))
	return list
"""
Returns a list of articles that were recently changed ([[Special:RecentChanges]])
If nponly = True, returns only newpages ([[Special:NewPages]])
"""
def recentchanges(limit = 500, nobot = True, onlyanon = False, hidepatrolled = True, nponly = False, wiki=config.wiki):
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
	list = []
	for page in res:
		list.append(wiki.Page(page['title']))

	return list

"""
Returns links on a provided page
Not Special:WhatLinksHere
ns is an (optional) int() which is the only namespace returned
"""
def links(page, ns=None):
	API = wiki.API(wiki=page.site())
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
	newlist = []
	for page in list:
		newlist.append(wiki.Page(page['title']))
	return newlist

def whatlinkshere(page):
	API = wiki.API(wiki=page.site())
	params = {
		'action':'query',
		'bltitle':page.title(),
		'list':'backlinks',
		'bllimit':'max',
	}
	res = API.query(params)['query']['backlinks']
	list = []
	for i in res:
		list.append(wiki.Page(i['title']))
	return list
	

"""
Picks the generator per argument passed in command line
Usage:
gen = pagegen.handleArgs()
for page in gen:
	...do something
"""
def handleArgs():
	for arg in wiki.getArgs():
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
