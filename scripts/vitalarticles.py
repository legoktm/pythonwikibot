#!/usr/bin/env python
# -*- coding: utf-8  -*-
#
# (C) Legoktm 2008-2009
# 
import re
import wiki
wiki.setUser('Legobot')
from wiki import pagegen
def do_page(page, text):
	try:
		print unicode(page)
		try:
			pagetext = page.get()
		except wiki.IsRedirectPage, e: #wtf...
			return text
		talkpage = page.toggletalk()
		talktext = talkpage.get()
		#get all of the classes and actions
		pgclass = ['','']
		try:
			pgclass[0] = wiki.parseTemplate(talktext)['class']
			if pgclass[0].lower() == 'fa':
				pgclass = ['FA','FA']
			elif pgclass[0].lower() == 'ga':
				pgclass = ['GA','GAicon']
			else:
				pgclass = [pgclass[0].title(), pgclass[0].title()+'-icon']
		except KeyError:
			print "No class assigned to %s." %str(page) #it cant find 'class='
			return text
		classes = ['fa','ga','a','b','c','stub','start']
		if not (pgclass[0].lower() in classes):
			pgclass = oldclassdetection(talktext)
			if not pgclass:
				return text
		print str(page) + " has a class of " + str(pgclass[0])
		#Check for FGANs, FFAs, and FFACs
		talkcats = talkpage.categories(raw=True)
		if 'Category:Wikipedia featured article candidates (contested)' in talkcats:
			pgclassother = ['FFAC', '{{FAC-icon}}']
		elif 'Category:Former good article nominees' in talkcats:
			pgclassother = ['FGAN','{{NoGA-icon}}']
		elif 'Category:Wikipedia former featured articles' in talkcats:
			pgclassother = ['FFA', '{{NoFA}}']
		else:
			pgclassother = ['','']
		pgtemp = pgclass[1]
		pgaltclass = pgclassother[1]
		#substitute it in.
		find = u'\{\{%s\}\} \[\[%s\]\]' %(pgtemp, page.title())
		shouldfind = u'{{%s}} [[%s]]' %(pgtemp, page.title())
#		print wikitext
		m=re.findall(find, text)
		try:
			print m[0]
			if m[0] == shouldfind:
				print '[[WP:VA]] does not need updating for %s' %page.aslink()
				return text
		except IndexError:
			print 'Not found, updating [[WP:VA]]'
		"""Following checks if the article is bolded"""
		boldcheck=re.findall("'''\[\[%s\]\]'''" %(page.title(regex=True)), text)
		try:
			boldcheck[0]
			bold=True
		except IndexError:
			print 'Not found'
			bold=False
		"""Done checking for bolding"""
		"""Check for howmany # signs, only checks for 3"""
		numcheck1=re.findall('\n(.*?) (.*?)\[\[%s\]\]' %(page.title(regex=True)), text)
		try:
			numcheck=numcheck1[0][0]
		except IndexError:
			return text #wtf???
		print numcheck
		find2= '(\{\{(.*)\}\}|) \[\[%s\]\]' %(str(page.title(regex=True)))
		if bold:
			find3= "%s(.*?)'''\[\[%s\]\]'''" %(numcheck, str(page.title(regex=True)))
			rep= "%s %s{{%s}} '''[[%s]]'''" %(numcheck, pgaltclass, pgtemp, str(page.title(regex=True)))
		else:
			find3= '%s(.*?)\[\[%s\]\]' %(numcheck, str(page.title(regex=True)))
			rep= '%s %s{{%s}} [[%s]]' %(numcheck, pgaltclass, pgtemp, str(page.title(regex=True)))
		text = re.sub(find3, rep, text)
		text = re.sub(find2, shouldfind, text)
		return text
	except UnicodeEncodeError:
		return text
	except UnicodeDecodeError:
		return text
def oldclassdetection(talktext):
	pgclass = None
	if re.search('class=FA',talktext,re.I):
		if not re.search('class=fail',talktext,re.I):
			pgclass = ['FA', 'FA']
	if re.search('class=A',talktext,re.I):
		pgclass = ['A', 'A-icon']
	elif re.search('class=GA',talktext,re.I):
		pgclass = ['GA', 'GAicon']
	elif re.search('class=B',talktext,re.I):
		pgclass = ['B', 'B-icon']
	elif re.search('class=C',talktext,re.I):
		pgclass = ['C', 'C-icon']
	elif re.search('class=stub',talktext,re.I):
		pgclass = ['Stub', 'Stub-icon']
	elif re.search('class=start',talktext,re.I):
		pgclass = ['Start', 'Start-icon']
	if not pgclass:
		print 'Can\'t find class????'
		return
	return pgclass

def get_pages():
	vapage = wiki.Page('Wikipedia:Vital articles')
	gen = pagegen.links(vapage, ns=0) #we only need mainspace articles
	text = state0 = vapage.get()
	num = 0
	for page in gen:
		if page.namespace() == 0:
			text = do_page(page, text)
	wiki.showDiff(state0, text)
	vapage.put(text, 'Bot: Updating Vital Articles', bot=True)
if __name__ == '__main__':
	get_pages()
