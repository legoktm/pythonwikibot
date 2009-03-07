#!usr/bin/env python
# -*- coding: utf-8 -*-
"""

Custom library for interfacing with MediaWiki through API

Released under the MIT License
(C) Legoktm 2008-2009
See COPYING for full License

"""
import urllib2, urllib, re, time, getpass, cookielib
from datetime import datetime
import config
import simplejson, sys, os, difflib, StringIO, hashlib
try:
	import gzip
except ImportError:
	gzip = False

class APIError(Exception):
	"""General API error and base class for all errors"""

class NotLoggedIn(APIError):
	"""User is not logged in"""

class UserBlocked(APIError):
	"""User is blocked"""

class LockedPage(APIError):
	"""Page is protected and user doesn't have right to edit"""

class MoveFailed(APIError):
	"""Move fails for any reason"""

class NoPage(APIError):
	"""Page does not exist"""

class IsRedirectPage(APIError):
	"""Page is a redirect to target"""

class NotCategory(APIError):
	"""When expected page should be category, but is not"""

class LoginError(APIError):
	"""General login error"""

class WrongPass(LoginError):
	"""Wrong password entered"""
	
class LoginThrottled(LoginError):
	"""Login throttled by MediaWiki"""

class NoUsername(APIError):
	"""No username given in userconfig.py"""

class Maxlag(APIError):
	"""Maxlag is too high"""
class MySQLError(Exception):
	"""Base class for all MySQL errors"""

class NoTSUsername(NoUsername):
	"""No Toolserver username given, but trying to use MySQL class"""

class API:
	
	def __init__(self, wiki = config.wiki, login=False, debug=False, qcontinue = True, maxlag = config.maxlag):
		#set up the cookies
		try:
			self.username = UserName
		except:
			self.username = config.username
		self.COOKIEFILE = config.path + '/cookies/'+ self.username +'.data'
		self.COOKIEFILE = self.COOKIEFILE.replace(' ','_')
		self.cj = cookielib.LWPCookieJar()
		if os.path.isfile(self.COOKIEFILE):
			self.cj.load(self.COOKIEFILE)
		elif not login:
			raise NotLoggedIn('Please login by first running wiki.py')
		if wiki == 'commons':
			self.wiki = 'commons.wikimedia'
		else:
			self.wiki = wiki
		self.login = login
		self.debug = debug
		self.qcontinue = qcontinue
		self.maxlag = maxlag
	def query(self, params, write = False, maxlagtries = 0):
		self.maxlagtries = maxlagtries
		self.write = write
		if os.path.isfile(self.COOKIEFILE):
			self.cj.load(self.COOKIEFILE)
		self.params = params
		self.params['format'] = 'json'
		if self.write:
			self.params['maxlag'] = self.maxlag
		self.encodeparams = urllib.urlencode(self.params)
		if self.debug:
			print self.encodeparams
		self.headers = {
			"Content-type": "application/x-www-form-urlencoded",
			"User-agent": config.username,
			"Content-length": len(self.encodeparams),
		}
		if gzip:
			self.headers['Accept-Encoding'] = 'gzip'
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(self.opener)
		self.request = urllib2.Request(config.apipath %(self.wiki), self.encodeparams, self.headers)
#		print 'Querying API'
		try:
			self.response = urllib2.urlopen(self.request)
		except urllib2.URLError, e:
			raise APIError('urllib2.URLError:' + str(e))
		if self.login:
			self.cj.save(self.COOKIEFILE)
#			self.cj.save(self.COOKIEFILE + 'old')
		text = self.response.read()
		if gzip:
			compressedstream = StringIO.StringIO(text)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			data = gzipper.read()
			#print data
		else:
			data = text
		
		newtext = simplejson.loads(data)
		#errors should be handled now
		try:
			if newtext.has_key('error'): #so that way write errors are handled seperatly
#				print nextext
				if newtext['error']['code'] == 'maxlag':
					print newtext ['error']['info']
					self.maxlagtries += 1
#					if self.maxlagtries >= 100:
#						raise Maxlag('Maxlag is too high right now.  Please try later')
					time.sleep(5)
					newtext = self.query(self.params, self.write, self.maxlagtries)
				elif not (self.login or self.write):
					raise APIError(newtext)
		except AttributeError:
			raise APIError(newtext)
		#finish query-continues
		if ('query-continue' in newtext) and self.qcontinue:
			newtext = self.__longQuery(newtext)
		return newtext
	def __longQuery(self, firstres):
		total = res = firstres
		params = self.params
		numkeys = len(res['query-continue'].keys())
		while numkeys > 0:
			keylist = res['query-continue'].keys()
			keylist.reverse()
			key1 = keylist[0]
			key2 = res['query-continue'][key1].keys()[0]
			if isinstance(res['query-continue'][key1][key2], int):
				cont = res['query-continue'][key1][key2]
			else:
				cont = res['query-continue'][key1][key2].encode('utf-8')
			params[key2] = cont
			print 'Continuing Query'
			res = API(qcontinue=False).query(params)
			for type in keylist:
				total = self.__resultCombine(type, total, res)
			if 'query-continue' in res:
				numkeys = len(res['query-continue'].keys())
			else:
				numkeys = 0
		return total
	def __resultCombine(self, type, old, new):
		"""
		Experimental-ish result-combiner thing
		If the result isn't something from action=query,
		this will just explode, but that shouldn't happen hopefully?
		(taken from python-wikitools)
		"""
		ret = old
		if type in new['query']: # Basic list, easy
			ret['query'][type].extend(new['query'][type])
		else: # Else its some sort of prop=thing and/or a generator query
			for key in new['query']['pages'].keys(): # Go through each page
				if not key in old['query']['pages']: # if it only exists in the new one
					ret['query']['pages'][key] = new['query']['pages'][key] # add it to the list
				else:
					for item in new['query']['pages'][key][type]:
						if item not in ret['query']['pages'][key][type]: # prevent duplicates
							ret['query']['pages'][key][type].append(item) # else update the existing one
		return ret

class Page:
	
	def __init__(self, page, wiki = config.wiki):
		self.API = API()
		self.page = unicode(page)
		self.wiki = wiki
		self.Site = Site(wiki=self.wiki)
		self.content = False
		self._basicinfo = False
		self.langlinks = False
		self.prot = False
		self.edittoken = False
		self.movetoken = False
		self.starttimestamp = False
		self.ns = False
		self.revisions = False
	def __str__(self):
		return self.page
	def __repr__(self):
		return 'Page{\'%s\'}' %self.page
	def __basicinfo(self):
		if self._basicinfo:
			return
		params = {
			'action':'query',
			'prop':'info|revisions|langlinks|categoryinfo',
			'titles':self.page,
			'inprop':'protection|talkid|subjectid',
			'intoken':'edit|move',
			'rvprop':'user|comment|content',
			'lllimit':'max',
		}
		self.res = self.API.query(params)['query']
		res2 = self.res['pages']
		self.id = str(res2.keys()[0])
		self._basicinfo = res2[self.id]
		try:
			self.revisions = self._basicinfo['revisions']
			self.content = self._basicinfo['revisions'][0]['*']
		except:
			if self._basicinfo.has_key('missing'):
				self.exist = False
			else:
				raise APIError(self._basicinfo)
		
		try:
			self.langlinks = self._basicinfo['langlinks']
		except:
			self.langlinks = None
		self.prot = self._basicinfo['protection']
		self.edittoken = self._basicinfo['edittoken']
		self.ns = self._basicinfo['ns']
		try:
			self.movetoken = self._basicinfo['movetoken']
		except:
			if self.res.has_key('warnings'):
				if self.res['warnings']['info']['*'] == 'Action \'move\' is not allowed for the current user':
					raise NotLoggedIn
		self.starttimestamp = self._basicinfo['starttimestamp']
		
		return self._basicinfo
	def title(self):
		return self.page
	def get(self, force = False):
		if self.isRedirect() and (not force):
			raise IsRedirectPage(self.API.query({'action':'query','titles':self.page,'redirects':''})['query']['redirects'][0]['to'])
		if int(self.id) == (-1 or -2):
			raise NoPage(self.page)
		if not self.content:
			self.__basicinfo()
		self.content = self.content.encode('utf-8')
		return self.content
	def __updatetime(self):
		#check if we have waited 10 seconds since the last edit/move 
		FILE = config.path + '/cookies/lastedit.data'
		try:
			text = open(FILE, 'r').read()
			split = text.split('|')
			date = datetime(int(split[0]), int(split[1]), int(split[2]), int(split[3]), int(split[4]), int(split[5]))
		except IOError:
			date = datetime.now()
		delta = datetime.now() - date
		if delta.seconds < 10:
			print 'Sleeping %s seconds' %(10-delta.seconds)
			time.sleep(10-delta.seconds)
		else:
			print 'Last editted %s seconds ago.' %delta.seconds
			print 'Sleeping for 2 seconds'
			time.sleep(2)
		#update the file
		d = datetime.now()
		newtext = str(d.year) +'|'+ str(d.month) +'|'+ str(d.day) +'|'+ str(d.hour) +'|'+ str(d.minute) +'|'+ str(d.second)
		write = open(FILE, 'w')
		write.write(newtext)
		write.close()	
	def put(self, newtext, summary=False, watch = False, newsection = False):
		#set the summary
		if not summary:
			try:
				summary = EditSummary
			except NameError:
				summary = '[[WP:BOT|Bot]]: Automated edit' 
		md5 = hashlib.md5(newtext).hexdigest()
		params = {
			'action':'edit',
			'title':self.page,
			'text':newtext,
			'summary':summary,
			'token':self.edittoken,
			'starttimestamp':self.starttimestamp,
			'md5':md5,
		}
		print 'Going to change [[%s]]' %(self.page)
		if watch:
			params['watch'] = ''
		if newsection:
			params['section'] = 'new'
		self.__updatetime()
		res=self.API.query(params, write = True)
		if res.has_key('error'):
			if res['error']['code'] == 'protectedpage':
				raise LockedPage(res['error']['info'])
			raise APIError(res['error'])
		if res['edit']['result'] == 'Success':
			print 'Changing [[%s]] was successful.' %self.page
		else:
			print 'Changing [[%s]] failed.' %self.page
			raise APIError(res)
		
	def titlewonamespace(self):
		if not self.ns:
			self.__basicinfo()
		if self.ns == 0:
			return self.page
		else:
			return self.page.split(':')[1]
	def namespace(self):
		if not self.ns:
			self.__basicinfo()
		return self.ns

	def lastedit(self, prnt = False):
		if not self.revisions:
			self.__basicinfo()
		ret = self.revisions
		if prnt:
			print 'The last edit on %s was made by: %s with the comment of: %s.' %(page, ret['user'], ret['comment'])
		return ret
	def istalk(self):
		if not self.ns:
			self.__basicinfo()
		if self.ns != -1 or self.ns != -2:
			if self.ns%2 == 0:
				return False
			elif self.ns%2 == 1:
				return True
			else:
				sys.exit("Error: Python Division error")
		else:
			return False
	def toggletalk(self):
		try:
			nstext = self.page.split(':')[0]
		except:
			nstext = ''
		nsnum = self.Site.namespacelist()[1][nstext]
		if nsnum == -1 or nsnum == -2:
			print 'Cannot toggle the talk of a Special or Media page.'
			return Page(self.page)
		istalk = self.istalk()
		if istalk:
			nsnewtext = self.Site.namespacelist()[0][nsnum-1]
		else:
			nsnewtext = self.Site.namespacelist()[0][nsnum+1]
		tt = nsnewtext + ':' + self.page.split(':')[1]
		return Page(tt)
	def isCategory(self):
		return self.namespace() == 14
	def isImage(self):
		return self.namespace() == 6
	def isTemplate(self):
		return self.namespace() == 10
	def isRedirect(self):
		self.__basicinfo()
		if self._basicinfo.has_key('redirect'):
			self.redirect = True
		else:
			self.redirect = False
		return self.redirect
	def patrol(self, rcid):
		params = {
			'action':'patrol',
			'rcid':rcid,
			'token':self.edittoken
		}
		self.API.query(params)
	def exists(self):
		self.__basicinfo()
		if self._basicinfo.has_key('missing'):
			return False
		else:
			return True
	def move(self, newtitle, summary, movetalk = True):
		self.newtitle = newtitle.decode('utf-8').encode('utf-8')
		tokenparams = {
			'action':'query',
			'prop':'info',
			'intoken':'move',
			'titles':self.page
		}
		token = self.API.query(tokenparams)['query']['pages']
		token = token[token.keys()[0]]['movetoken']
		params = {
			'action':'move',
			'from':self.page,
			'to':self.newtitle,
			'reason':summary,
			'token':token,
			'movetalk':'',
		}
		self.__updatetime()
		res = self.API.query(params, write = True)
		if res.has_key('error'):
				if res['error']['code'] == 'articleexists':
					raise MoveFailed(res['error'])
				else:
					raise APIError(res['error'])	
		if res.has_key('move'):
			try:
				print 'Page move of %s to %s succeeded' %(self.page, self.newtitle.encode('utf-8'))
			except UnicodeDecodeError:
				print 'Page move of %s succeeded' %(self.page)
		return res
		
	def protectlevel(self):
		params = {'action':'query','titles':self.page,'prop':'info','inprop':'protection'}
		res = self.API.query(params)['query']['pages']
		list = res[res.keys()[0]]['protection']
		#check if the page is protected
		if len(list) == 0:
			#means the page isn't protected
			return {}
		retdict = {}
		for dict in list:
			if (dict['type'] == 'edit') and (not dict.has_key('source')):
				retdict['edit'] = {'level':dict['level'],'expiry':dict['expiry']}
			if (dict['type'] == 'move') and (not dict.has_key('source')):
				retdict['move'] = {'level':dict['level'],'expiry':dict['expiry']}
			if not (retdict.has_key('edit') or retdict.has_key('edit')):
				if (dict['type'] == 'edit'):
					retdict['edit'] = {'level':dict['level'],'expiry':dict['expiry'], 'cascaded':''}
				if (dict['type'] == 'move'):
					retdict['move'] = {'level':dict['level'],'expiry':dict['expiry'], 'cascaded':''}				
		return retdict
	def site(self):
		return self.wiki
	def categories(self):
		params = {'action':'query','titles':self.page,'prop':'categories'}
		res = self.API.query(params)['query']['pages']
		list = []
		for item in res[res.keys()[0]]['categories']:
			list.append(Page(item['title']))
		return list
	def templates(self):
		params = {'action':'query','titles':self.page,'prop':'templates','tllimit':'max'}
		res = self.API.query(params)['query']['pages']
		list = res[res.keys()[0]]['templates']
		rawlist = []
		for i in list:
			rawlist.append(i['title'])
		return rawlist
	def whatlinkshere(self, onlyredir = False):
		params = {'action':'query','list':'backlinks','bltitle':self.page,'bllimit':'max'}
		if onlyredir:
			params['blfilterredir'] = 'redirects'
		res = self.API.query(params)['query']['backlinks']
		list = []
		for id in res:
			title = id['title']
			list.append(Page(title))
		return list
	def redirects(self):
		return self.whatlinkshere(onlyredir = True)
	def purge(self):
		params = {'action':'purge','titles':self.page}
		res = self.API.query(params)
		try:
			if res['purge'][0].has_key('purged'):
				print '[[%s]] was succesfully purged.' %self.page
		except KeyError:
			raise APIError(res)
		except IndexError:
			raise APIError(res)
	def aslink(self, regex = False):
		if not regex:
			return '[[%s]]' %(self.page)
		reg =  '\[\[%s\]\]' %(self.page)
		self.reg = reg.replace('(','\(').replace(')','\)')
		return self.reg
"""
Class that is mainly internal working, but contains information relevant
to the wiki site.
"""
class Site:
	def __init__(self, wiki):
		self.wiki = wiki
		self.API = API(self.wiki)
	def namespacelist(self):
		params = {
			'action':'query',
			'meta':'siteinfo',
			'siprop':'namespaces',
		}
		res = API().query(params)
		resd = res['query']['namespaces']
		list = resd.keys()
		nstotext = {}
		texttons = {}
		for ns in list:
			nstotext[int(ns)] = resd[ns]['*']
			texttons[resd[ns]['*']] = int(ns)
		self.nslist = (nstotext,texttons)
		return self.nslist

"""
Other functions
"""
def checklogin():
	paramscheck = {
		'action':'query',
		'meta':'userinfo',
		'uiprop':'hasmsg',
	}
	querycheck = API().query(paramscheck)
	name = querycheck['query']['userinfo']['name']
	print name
	if querycheck['query']['userinfo'].has_key('messages'):
		print 'You have new messages on %s.' %(config.wiki)
		if config.quitonmess:
			sys.exit()
	if querycheck['query']['userinfo'].has_key('anon'):
		return False
	return name
def login(username = False):
	if not username:
		username = config.username
	try:
		password = config.password
	except:
		password = getpass.getpass('API Login Password for %s: ' %username)
	params = {
		'action' : 'login',
		'lgname' : username,
		'lgpassword' : password,
	}
	
	query = API(login=True).query(params)
	result = query['login']['result'].lower()
	if result == 'success':
		print 'Successfully logged in on %s.' %(config.wiki)
	elif result == 'wrongpass':
		raise WrongPass
	elif result == 'throttled':
		raise LoginThrottled('Wait %s seconds before trying again.' %(query['login']['wait']))
	else:
		print 'Failed to login on %s.' %(config.wiki)
		raise APIError(query)
def setAction(summary):
	global EditSummary
	EditSummary = summary

def setUser(name):
	global UserName
	UserName = name
	print 'Switching username to %s on %s.' %(UserName, config.wiki)

def showDiff(oldtext, newtext):
	"""
	Prints a string showing the differences between oldtext and newtext.
	"""
	for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
		if '-' == line[0]:
			print line
		elif '+' == line[0]:
			print line
	
if __name__ == "__main__":
	login()
try:
	x=sys.modules['wiki']
	print 'Logged in as %s on %s.' %(config.username, config.wiki)
except KeyError:
	#do nothing
	0