#!usr/bin/python
#
# (C) Legoktm 2009
# Released under the MIT License
#
# All pages should be in the wiki.Page() format
__version__ = '$Id$'

import wiki, config

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
			if type(recurse) is int:
				self.recurse = recurse
			elif type(recurse) is bool: #has to be true
				self.recurse = recurse
				self.rinfinite = True
			elif type(recurse) is str:
				try:
					recurse = int(recurse)
					self.recurse = recurse
				except:
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
		print 'Getting [[%s]]...' %self.page.title()
		res = self.API.query(self.params)['query']['categorymembers']
		list = []
		
def category(page):
	if not page.isCategory():
		raise wiki.NotCategory(page.title())
	API = wiki.API(wiki=page.site())
	print 'Getting [[%s]]...' %page.title()
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
		params['rctype'] = 'new'
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
	