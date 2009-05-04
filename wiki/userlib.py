#!usr/bin/python
# -*- coding: utf-8 -*-
import wiki
__version__ = '$Id$'
class User:
	def __init__(self, page):
		self.page = page
		self.title = page.title()
		self.id = page.id()
#		self.username = self.page.titlewonamespace()
		self.username = False
		self.API = wiki.API(wiki=page.getSite())
	def editcount(self):
		if not self.username:
			self.username = self.page.titlewonamespace()
		params = 'action=query&list=users&ususers=%s&usprop=editcount' %self.username
		try:
			return self.API.query(params)['query']['users'][0]['editcount']
		except KeyError:
			return 0
	def isBlocked(self):
		if not self.username:
			self.username = self.page.titlewonamespace()	
		params = 'action=query&list=users&ususers=%s&usprop=blockinfo' %self.username
		res = self.API.query(params)['query']['users'][0]
		if res.has_key('blockedby') or res.has_key('blockreason'):
			return True
		return False
	def Page(self):
		"""
		Returns the page object for the userpage
		"""
		return self.page
	def name(self):
		if not self.username:
			self.username = self.page.titlewonamespace()
		"""
		Returns the users name
		"""
		return self.username