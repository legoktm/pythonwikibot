#!usr/bin/python
import wiki

class Category:
	
	def __init__(self, page):
		self.page = page
		self.title = page.title()
		self.id = page.id
		self.API = wiki.API(wiki=page.getSite())
	def __str__(self):
		return self.page.aslink()
	def __repr__(self):
		return 'Category{\'%s\'}' %self.page.title()		
	def catinfo(self):
		params = {
			'action':'query',
			'titles':self.title,
			'prop':'categoryinfo',
		}
		res = self.API.query(params)['query']['pages'][self.id]['categoryinfo']
		return res
	def subcats(self, recurse=False):
		print 'Getting %s...' %self.page.aslink()	
		params = 'action=query&list=categorymembers&cmlimit=max&cmnamespace=14&cmtitle=' + self.title
		res = self.API.query(params)['query']['categorymembers']
		if not isinstance(recurse, bool) and recurse:
			recurse = recurse - 1
		if not hasattr(self, "_subcats"):
			self._subcats = []
			for i in res:
				subcat = Category(wiki.Page(i['title'], wiki=self.page.getSite()))
				self._subcats.append(subcat)
				yield subcat
				if recurse:
					for i in subcat.subcats(recurse):
						yield i
	
		