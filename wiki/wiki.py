#!usr/bin/python
# -*- coding: utf-8 -*-
"""

Custom library for interfacing with MediaWiki through API

Released under the MIT License
(C) Legoktm 2008-2009
See COPYING for full License

"""

__version__ = '$Id$'
import urllib2, urllib, re, time, getpass, cookielib
from urllib import quote_plus, _is_unicode
from datetime import datetime
import config, timedate, families
import sys, os, difflib, hashlib
import BeautifulSoup as BS
try:
	import gzip, StringIO
except ImportError, e:
	print 'WARNING: Please install %s to save bandwith costs.' %(str(e).split('named ')[1])
	time.sleep(1)
	gzip = False
try:
	import json as simplejson
except ImportError:
	import simplejson

reload(sys)
sys.setdefaultencoding('utf-8')

class APIError(Exception):
	"""General API error and base class for all errors"""

class NoWiki(APIError):
	"""Wiki Specified doesn't have an entry in families.py"""

class NotLoggedIn(APIError):
	"""User is not logged in"""

class UserBlocked(APIError):
	"""User is blocked"""

class NotAllowed(APIError):
	"""Tries preforming action without right"""
	
class LockedPage(NotAllowed):
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
	
	def __init__(self, wiki=False, login=False, loginu=False, qcontinue = True, maxlag = config.maxlag, url=False):
		#set up the cookies
		if not wiki:
			wiki = getWiki()
		global CJ
		if loginu:
			self.username = loginu
			self.COOKIEFILE = getPath() + '/wiki/cookies/'+ loginu +'-'+ str(wiki).replace('.','_') + '.data'
			CJ = cookielib.LWPCookieJar() #reset
		else:
			global COOKIEFILE
			self.COOKIEFILE = COOKIEFILE
		if os.path.isfile(self.COOKIEFILE):
			CJ.load(self.COOKIEFILE)
		if not wiki and not url:
			self.wiki = getWiki()
			self.api = False
		elif url:
			self.wiki = False
			self.api = wiki
		else:
			self.wiki = wiki
			self.api = False
		self.login = login
		global DebugValue
		self.debug = DebugValue
		self.qcontinue = qcontinue
		self.maxlag = maxlag
	def query(self, params, write = False, maxlagtries = 0, format='json'):
		global CJ
		self.maxlagtries = maxlagtries
		self.format = format
		if self.format != ('json' or 'xml'):
			self.format = 'json' #silently change it
		self.write = write
		self.params = params
		if type(self.params) == type({}):
			self.params['format'] = self.format
			self.pformat = 'dict'
		elif type(self.params) == type(''):
			self.params += '&format=' + self.format
			self.pformat = 'str'
		elif type(self.params) == type(u''):
			self.params += '&format=' + self.format
			self.pformat = 'str'
		else:
			raise APIError('Invalid Parameter format')
		if self.write:
			if self.pformat == 'dict':
				self.params['maxlag'] = self.maxlag
			elif self.pformat == 'str':
				self.params += '&maxlag=%s' %self.maxlag
		if self.pformat == 'dict':
			self.encodeparams = urlencode(self.params)
		else:
			self.encodeparams = self.params
		if self.debug and not (write or login):
			print self.encodeparams
		self.headers = {
			"Content-type": "application/x-www-form-urlencoded",
			"User-agent": config.username,
			"Content-length": len(self.encodeparams),
		}
		if not self.api:
			self.api = self.wiki.getAPI()
		if gzip:
			self.headers['Accept-Encoding'] = 'gzip'
		try:
			del url
		except UnboundLocalError:
			0 #nothing
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ))
		urllib2.install_opener(self.opener)
		self.request = urllib2.Request(self.api, self.encodeparams, self.headers)
#		print 'Querying API'
		try:
			self.response = urllib2.urlopen(self.request)
		except urllib2.URLError, e:
			raise APIError('urllib2.URLError:' + str(e))
		if self.login:
			CJ.save(self.COOKIEFILE)
			CJ.load(self.COOKIEFILE) #refresh
#			self.cj.save(self.COOKIEFILE + 'old')
		text = self.response.read()
		self.response.close()
		if gzip:
			compressedstream = StringIO.StringIO(text)
			gzipper = gzip.GzipFile(fileobj=compressedstream)
			data = gzipper.read()
			#print data
		else:
			data = text
		
		if self.format == 'json':
			newtext = simplejson.loads(data)
		elif self.format == 'xml':
			newtext = BS.BeautifulStoneSoup(data)
			
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
	"""
	A wiki.Page() object.
	page = page title whether as plain text or [[wikilinked]]. (REQUIRED)
	wiki = which site is the page on? A Site() object given by getWiki() (OPTIONAL)
	id = id of the page, will be used rather than the page value (optional)
	"""
	def __init__(self, page, wiki=False, id =False):
		if not wiki:
			wiki = getWiki()
		self.API = API(wiki=wiki)
		if '[[' in page:
			self.page = unicode(re.findall('\[\[(.*?)\]\]', page)[0])
		elif '{{' in page:
			self.page = unicode('Template:' + re.findall('\{\{(.*?)\}\}', page)[0].split('|')[0])		
		else:
			self.page = unicode(page)
		self.stid = id
		self.wiki = wiki
		self.content = False
		self._basicinfo = False
		self.langlinks = False
		self.prot = False
		self.edittoken = False
		self.movetoken = False
		self.starttimestamp = False
		self.ns = False
		self.revisions = False
		self.deletetoken = False
		self.protecttoken = False
		self.traffic = False
		self.oppid = False
#		self.site = Site(wiki=self.wiki)
		if self.stid:
			self.__basicinfo()
	def __str__(self):
		return self.aslink()
	def __repr__(self):
		return 'Page{\'%s\'}' %self.page
	def __basicinfo(self):
		if self._basicinfo:
			return
		params = {
			'action':'query',
			'prop':'info|revisions|langlinks|categoryinfo',
			'inprop':'protection|talkid|subjectid',
			'intoken':'edit|move|delete|protect', #even if not admin, just get them...
			'rvprop':'user|comment|content|timestamp',
			'lllimit':'max',
		}
		if self.stid:
			params['pageids'] = self.stid
		else:
			params['titles'] = self.page.encode('utf-8')
		
		res = self.API.query(params)
		try:
			self.res=res['query']
		except KeyError:
			try:
				warnings = res['warnings']['query']['*']
				raise APIError(warnings)
			except KeyError:
				raise APIError(res) #wtf..
		res2 = self.res['pages']
		self.id = str(res2.keys()[0])
		self._basicinfo = res2[self.id]
		if self.stid:
			self.page = self._basicinfo['title']
		try:
			self.revisions = self._basicinfo['revisions'][0]
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
		try:
			self.oppid = self._basicinfo['talkid']
		except KeyError:
			try:
				self.oppid = self._basicinfo['subjectid']
			except KeyError:
				self.oppid = None #opposite page doesent exist
		self.prot = self._basicinfo['protection']
		self.edittoken = self._basicinfo['edittoken']
		self.ns = self._basicinfo['ns']
		if self.res.has_key('warnings'):
			self.warnings = self.res['warnings']['info'].split('\n')
			for i in self.warnings:
				if i == 'Action \'move\' is not allowed for the current user':
					self.movetoken = 'NO'
				if i == 'Action \'delete\' is not allowed for the current user':
					self.deletetoken = 'NO'
				if i == 'Action \'protect\' is not allowed for the current user':
					self.protecttoken = 'NO'
				if i == 'Action \'edit\' is not allowed for the current user':
					self.edittoken = 'NO'
		try:
			self.movetoken = self._basicinfo['movetoken']
		except:
			self.movetoken = 'NO'
		try:
			self.edittoken = self._basicinfo['edittoken']
		except:
			self.edittoken = 'NO'
		try:
			self.protecttoken = self._basicinfo['protecttoken']
		except:
			self.protecttoken = 'NO'
		try:
			self.deletetoken = self._basicinfo['deletetoken']
		except:
			self.deletetoken = 'NO'
			
		self.starttimestamp = self._basicinfo['starttimestamp']
		
		return self._basicinfo
	def title(self, regex=False):
		"""
		Returns a unicode string of the page title.
		"""
		if not regex:
			return self.page
		return self.page.replace('(','\(').replace(')','\)')
	def get(self, force = False):
		"""
		Returns the wikitext of the page.
		It will raise an error if the page is a redirect
		and force is not True.
		"""
		if self.isRedirect() and (not force):
			raise IsRedirectPage(self.getredirecttarget())
		if int(self.id) < 0:
			raise NoPage(self.page)
		if not self.content:
			self.__basicinfo()
		self.content = self.content.encode('utf-8')
		return self.content
	def getredirecttarget(self):
		"""
		Returns a Page() object of the
		targed of the redirect.
		"""
		if not self.isRedirect():
			return False
		return Page(self.API.query({'action':'query','titles':self.page,'redirects':''})['query']['redirects'][0]['to'])
	def __updatetime(self):
		#check if we have waited 10 seconds since the last edit/move 
		FILE = getPath() + '/wiki/cookies/lastedit.data'
		try:
			textfile = open(FILE, 'r')
			text = textfile.read()
			textfile.close() #if we dont, and you make over 2000 edits, crashes w/ to many files open
			split = text.split('|')
			date = datetime(int(split[0]), int(split[1]), int(split[2]), int(split[3]), int(split[4]), int(split[5]))
		except IOError:
			date = datetime.now()
		delta = datetime.now() - date
		if delta.seconds < PutThrottle:
			print 'Sleeping %s seconds' %(PutThrottle-delta.seconds)
			time.sleep(PutThrottle-delta.seconds)
		else:
			print 'Last editted %s seconds ago.' %delta.seconds
			print 'Sleeping for %s seconds' %PutThrottle
			time.sleep(PutThrottle)
		#update the file
		d = datetime.now()
		newtext = str(d.year) +'|'+ str(d.month) +'|'+ str(d.day) +'|'+ str(d.hour) +'|'+ str(d.minute) +'|'+ str(d.second)
		write = open(FILE, 'w')
		write.write(newtext)
		write.close()
		#check whether we need to quit
		if config.quitonmess:
			global NumEdits
			if NumEdits == 5:
				checklogin()
				NumEdits = 0
			else:
				NumEdits += 1
	def put(self, newtext, summary=False, watch = False, newsection = False):
		"""
		Edits the wikipage.
		newtext = what to replace the text with (REQUIRED)
		summary = the edit summary (optional: can be set with setAction)
		watch = bool, whether the page should be added to the watchlist (optional: default false)
		newsection = bool, whether the newtext is added as a new section. (optional: default false)
		"""
		#set the summary
		if not summary:
			try:
				summary = EditSummary
			except NameError:
				summary = '[[WP:BOT|Bot]]: Automated edits using [[en:w:User:Legobot/PythonWikiBot|PythonWikiBot]]' 
		try:
			md5 = hashlib.md5(newtext).hexdigest() #for safety
		except:
			md5 = False
		if not self.edittoken:
			self.__basicinfo()
		if self.edittoken == 'NO':
			raise NotAllowed({'action':'edit','page':self.page})
		params = {
			'action':'edit',
			'title':self.page,
			'text':newtext,
			'summary':summary,
			'token':self.edittoken,
			'starttimestamp':self.starttimestamp,
			'assert':'user',
		}
		if md5:
			params['md5'] = md5
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
			elif res['error']['info'] == 'protectedpage': #wtf problem
				raise LockedPage(res['error']['code'])				
			raise APIError(res['error'])
		if res['edit']['result'] == 'Success':
			print 'Changing [[%s]] was successful.' %self.page
		else:
			print 'Changing [[%s]] failed.' %self.page
			raise APIError(res)
		
	def titlewonamespace(self):
		"""
		Returns a unicode string of the title
		without the namespace prefix.
		"""
		if not self.ns:
			self.__basicinfo()
		if self.ns == 0:
			return self.page
		else:
			return "".join(self.page.split(':')[1:])
	def namespace(self):
		"""
		Returns the namespace as an integer
		"""
		if not self.ns:
			self.__basicinfo()
		return self.ns

	def lastedit(self, prnt = False):
		"""
		Returns a dictionary with the info provided by
		prop=revisions
		rvprop=user|comment|content|timestamp
		"""
		if not self.revisions:
			self.__basicinfo()
		ret = self.revisions
		if prnt:
			print 'The last edit on %s was made by: %s with the comment of: %s at %s.' %(page, ret['user'], ret['comment'], ret['timestamp'])
		return ret
	def istalk(self):
		"""
		Returns True or False depending
		on whether the page is a talk page.
		"""
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
		"""
		Returns a Page object of the 
		article page or talk page
		"""
		if self.oppid == False:
			self.__basicinfo()
		if self.oppid != None: #talk page exists and has id
			return Page(page='', id=self.oppid, wiki=self.wiki)
		if self.isTalk():
			newns = self.ns-1
		else:
			newns = self.ns+1
		return Page(self.wiki.nslist()[newns] + ':' + self.titlewonamespace(),wiki=self.wiki)

	def isCategory(self):
		return self.namespace() == 14
	def isImage(self):
		return self.namespace() == 6
	def isTemplate(self):
		return self.namespace() == 10
	def isTalk(self):
		return self.istalk() #for name standardization
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
	def move(self, newtitle, reason=False, movetalk = True):
		self.newtitle = newtitle.decode('utf-8').encode('utf-8')
		if not self.movetoken:
			self.__basicinfo()
		if self.movetoken == 'NO':
			raise NotAllowed({'action':'move','page':self.page})
		params = {
			'action':'move',
			'from':self.page,
			'to':self.newtitle,
			'reason':summary,
			'token':self.movetoken,
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
	def getSite(self):
		return self.wiki
	def categories(self):
		params = {'action':'query','titles':self.page,'prop':'categories'}
		res = self.API.query(params)['query']['pages']
		list = []
		for item in res[res.keys()[0]]['categories']:
			list.append(Page(item['title'], wiki=self.wiki))
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
			list.append(Page(title, wiki=self.wiki))
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
	def aslink(self, regex = False, template = True):
		if not regex:
			return '[[%s]]' %(self.page)
		if self.isTemplate() and template:
			return '\{\{%s' %self.titlewonamespace()
		reg =  '\[\[%s\]\]' %(self.page)
		self.reg = reg.replace('(','\(').replace(')','\)')
		return self.reg
	def delete(self, reason=False): #ADMIN ONLY FUNCTION
		if not reason:
			try:
				summary = EditSummary
			except:
				summary = None
		else:
			summary = reason
		if not self.deletetoken:
			self.__basicinfo()
		if self.deletetoken == 'NO':
			raise NotAllowed({'action':'delete','page':self.page})
		self.__updatetime() #slow us down
		params = {
			'action':'delete',
			'title':self.page,
			'token':self.deletetoken
		}
		if summary:
			params['reason'] = summary
		self.API.query(params, write = True) #TODO: implement error checking
	def NumberofRevisions(self): #returns the number of revisions
		params = 'action=query&prop=revisions&titles=%s&rvlimit=max' %self.page
		res = self.API.query(params)['query']['pages']
		try:
			self.fullrevisions = res[res.keys()[0]]['revisions']
		except KeyError:
			return 0
		return len(self.fullrevisions)
	def ArticleTraffic(self, force=False):
		if self.traffic and not force:
			return self.traffic
		year = str(time.gmtime().tm_year)
		month = timedate.numwithzero(time.gmtime().tm_mon)
		url = 'http://stats.grok.se/en/%s%s/%s' %(year, month, self.page)
		open = urllib.urlopen(url)
		text = open.read()
		open.close() # :P
		self.traffic = int(re.findall('viewed (.*?) times',text)[0])
		return self.traffic
	def id(self):
		if not self.id:
			self.__basicinfo()
		return self.id
class Site:
	"""
	A wiki site
	"""
	def __init__(self, url):
		self.shorturl = url
		try:
			self.wiki = families.wikilist[url]
		except KeyError:
			raise NoWiki(url)
		self.apiurl = self.wiki['baseurl'] + self.wiki['api']
		self.indexurl = self.wiki['baseurl'] + self.wiki['index']
		self.API = False
		self.nslist1 = False
		self.nsretdict = False
	def __basicinfo(self):
		params = 'action=query&meta=siteinfo&siprop=namespaces|namespacealiases|general'
		if not self.API:
			self.API = API(url=self.apiurl)
		self.basicinfo = self.API.query(params)['query']
		self.nslist1 = self.basicinfo['namespaces']
		self.__handlenslist()
	def __handlenslist(self):
		if not self.nslist1:
			self.__basicinfo()
		if self.nsretdict:
			return
		self.nsretdict = {}
		for key in self.nslist1.keys():
			self.nsretdict[int(key)] = self.nslist1[key]['*']
	def nslist(self):
		if not self.nsretdict:
			self.__basicinfo()
		return self.nsretdict
	def getAPI(self):
		return self.apiurl
	def getIndex(self):
		return self.indexurl
	def __str__(self):
		return self.shorturl
	def __repr__(self):
		return self.shorturl
	def langcode(self):
		return self.wiki['code']


def getWiki(url=False):
	if url:
		return Site(url)
	return Site(config.wiki)
def setWiki(url):
#	print 'Changing wiki to ' + url
	config.wiki = url
"""
Other functions
"""
def checklogin():
	"""
	Checks whether the bot is logged in.
	It will not check if it is a certain user, but not an anon.
	Also checks whether you have new messages.
	"""
	paramscheck = {
		'action':'query',
		'meta':'userinfo',
		'uiprop':'hasmsg',
	}
	querycheck = API().query(paramscheck)
	name = querycheck['query']['userinfo']['name']
	if querycheck['query']['userinfo'].has_key('messages'):
		print 'You have new messages on %s.' %(config.wiki)
		if config.quitonmess:
			sys.exit()
	if querycheck['query']['userinfo'].has_key('anon'):
		return False
	return name
def login(username = False, prompt = False):
	"""
	Used to log a user in to the wiki.
	username = specifies username to login with (optional)
	prompt = whether to prompt for username (optional)
	"""
	if not username and not prompt:
		username = config.username
	if prompt:
		username = raw_input('Username: (blank if %s) ' %config.username)
		if len(username) == 0:
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
	
	query = API(login=True, loginu=username).query(params)
	password = [] #so it can't be used again
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
def getArgs(args=False):
	"""
	Gets the arguments passed when running
	from command line.
	Needed so it will remove global args 
	"""
	if type(args) == type(''):
		args = args.split(' ')
	if not args:
		args = sys.argv[1:]
	arglist = []
	for arg in args:
		if arg.startswith('-user:'):
			setUser(arg[6:])
		elif arg.startswith('-pt:'):
			setThrottle(int(arg[4:]))
		elif arg.startswith('-site:'):
			setWiki(arg[6:])
		elif arg.startswith('-wiki:'):
			setWiki(arg[6:])
		elif arg == '-debug':
			setDebug(True)
			print config.wiki
		else: #not a global arg
			arglist.append(arg)
	return arglist
def setAction(summary):
	"""
	Set's global edit summary.
	A provided summary will overide this.
	Will be set until the script is killed,
	or setAction() is called again.
	"""
	global EditSummary
	EditSummary = summary

def setThrottle(num):
	"""
	Sets the put throttle
	If num < 3: then it defaults to 10 due
	to overloading a wiki.
	"""
	global PutThrottle
	PutThrottle = int(num)
def setUser(name):
	"""
	Set's the username that will be used
	for all queries and actions.
	NOTE: You must have already logged in as this
	user to make an API call.
	"""
	global UserName
	UserName = name
#	print 'Switching username to %s on %s.' %(UserName, config.wiki)
	global COOKIEFILE #update it
	COOKIEFILE = getPath() + '/wiki/cookies/'+ getUser() +'-'+ str(config.wiki).replace('.','_') + '.data'
def getPath():
	global real_dir
#	if real_dir == config.path:
#		return config.path
	dir = config.path
	for arg in sys.argv:
		if arg.startswith('-dir:'):
			dir = arg[5:]
			sys.argv.remove(arg)
			break
	else:
		if os.environ.has_key('PYTHONWIKIBOT'):
			dir = os.environ['PYTHONWIKIBOT']
		else:
			if os.path.exists('scripts/'):
				dir = config.path
			else:
				try:
					dir = os.path.split(os.path.abspath(sys.modules['config'].__file__))[0]
				except KeyError:
					pass
	real_dir = dir
	return dir
def getUser():
	"""
	Returns the username that has been set by setUser()
	or in the userconfig.py
	"""
	global UserName
	try:
		return UserName
	except:
		return config.username
def setDebug(value = False):
	global DebugValue
	DebugValue = value
def showDiff(oldtext, newtext):
	"""
	Prints a string showing the differences between oldtext and newtext.
	"""
	for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
		if '-' == line[0]:
			print line
		elif '+' == line[0]:
			print line

def parseTemplate(str):
	"""
	Parses the provided string
	and returns a dict with keys being parameters,
	and value's being the value of the named parameter.
	It will not pick up on non-named parameters.
	"""
	str = str.replace(' ', '_').replace('|', ' |') #so that \s catches it
	str = str.replace('}}', ' }}') #last param is caught by \s
	regex = re.compile("(?P<key>\w*?)=(?P<value>\w*?)\s|$", re.MULTILINE)
	ret = {}
	findall = []
	for line in str.splitlines():
		findall.extend(regex.findall(str))
	for i in findall:
		if len(i[0]) != 0:
			if not ret.has_key(i[0]):
				ret[i[0]] = i[1]
	return ret

def getURL(url, headers=False):
	if not headers:
		headers = {'User-agent':getUser()}
	request = urllib2.Request(url, headers=headers)
	response = urllib2.urlopen(request)
	text = response.read()
	response.close()
	return urllib.unquote(text)
def translate(dict):
	try:
		return dict[getWiki().langcode()]
	except KeyError:
		try:
			return dict['en'] #default to english
		except KeyError:
			return dict[dict.keys()[0]] #last resort
def urlencode(query,doseq=0):
	"""
	Hack of urllib's urlencode function, which can handle
	utf-8, but for unknown reasons, chooses not to by 
	trying to encode everything as ascii
    """

	if hasattr(query,"items"):
		# mapping objects
		query = query.items()
	else:
		# it's a bother at times that strings and string-like objects are
		# sequences...
		try:
			# non-sequence items should not work with len()
			# non-empty strings will fail this
			if len(query) and not isinstance(query[0], tuple):
				raise TypeError
			# zero-length sequences of all types will get here and succeed,
			# but that's a minor nit - since the original implementation
			# allowed empty dicts that type of behavior probably should be
			# preserved for consistency
		except TypeError:
			ty,va,tb = sys.exc_info()
			raise TypeError, "not a valid non-string sequence or mapping object", tb

	l = []
	if not doseq:
		# preserve old behavior
		for k, v in query:
			k = quote_plus(str(k))
			try:
				v = quote_plus(str(v.encode('utf-8')))
			except:
				try:
					v = quote_plus(str(v))
				except:
					v = quote_plus(unicode(v))
			l.append(k + '=' + v)
	else:
		for k, v in query:
			k = quote_plus(str(k))
			if isinstance(v, str):
				v = quote_plus(v)
				l.append(k + '=' + v)
			elif _is_unicode(v):
				# is there a reasonable way to convert to ASCII?
				# encode generates a string, but "replace" or "ignore"
				# lose information and "strict" can raise UnicodeError
				v = quote_plus(v.encode("utf8","replace")) #this is what is changed.. ACSII->utf8
				l.append(k + '=' + v)
			else:
				try:
					# is this a sufficient test for sequence-ness?
					x = len(v)
				except TypeError:
					# not a sequence
					v = quote_plus(str(v))
					l.append(k + '=' + v)
				else:
					# loop over the sequence
					for elt in v:
						l.append(k + '=' + quote_plus(str(elt)))
	return '&'.join(l)

#set some defaults
PutThrottle = 10
NumEdits = 5
DebugValue = False
getArgs() #so it gets site.. throttles...
real_dir = config.path
real_dir = getPath()
#print this when imported
print 'Operating as %s on %s.' %(getUser(), config.wiki) #why is it printing twice??
#fix all of the cookiefile stuff
COOKIEFILE = getPath() + '/wiki/cookies/'+ getUser() +'-'+ str(config.wiki).replace('.','_') + '.data'
COOKIEFILE = COOKIEFILE.replace(' ','_')
CJ = cookielib.LWPCookieJar()
if os.path.isfile(COOKIEFILE):
	CJ.load(COOKIEFILE)

if __name__ == "__main__":
    import version
    version.main()
    print 'PythonWikiBot release 0.1'
    print '(C) 2008-2009 PythonWikiBot team MIT License'
    login(prompt=True)
