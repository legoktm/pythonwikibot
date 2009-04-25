#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# (C) Legoktm 2008-2009
# 
import re
from pywikibot import wiki, pagegen

def do_page(page, text):
	try:
		print unicode(page)
		try:
			pagetext = page.get()
		except wiki.IsRedirectPage, e: #wtf...
			return text
		talktext = page.toggletalk().get()
		#get all of the classes and actions
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
		else:
			print "No class assigned to %s." %str(page)
			return text
		print str(page) + " has a class of " + str(pgclass[0])
		#Check for FGANs, FFAs, and FFACs
		ffac=re.findall('action(.*?)=FAC', pagetext)
		ffar=re.findall('action(.*?)=FAR', pagetext)
		pgclassother = False
		for i in ffac:
			if re.search('action%sresult=not promoted' %(i),text,re.I):
				pgclassother = ['FFAC', '{{FAC-icon}}']
		if re.search('currentstatus=FGAN',text,re.I):
			pgclassother = ['FGAN','{{NoGA-icon}}']
		if re.search('currentstatus=FFA',text,re.I):
			pgclassother = ['FFA', '{{NoFA}}']
		for i in ffar:
			if re.search('action%sresult=demoted' %(i),text,re.I):
				pgclassother = ['FFAC', '{{FAC-icon}}']
		if not pgclassother:
			pgclassother = ['','']

		pgtemp = pgclass[1]
		pgaltclass = pgclassother[1]
		#substitute it in.
		find = u'\{\{%s\}\} \[\[%s\]\]' %(pgtemp, page.title())
		shouldfind = u'{{%s}} [[%s]]' %(pgtemp, page.title())
		print find
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
			print boldcheck[0]
			bold=True
		except IndexError:
			print 'Not found'
			bold=False
		"""Done checking for bolding"""
		"""Check for howmany # signs, only checks for 3"""
		numcheck1=re.findall('\n(.*?) (.*?)\[\[%s\]\]' %(page.title(regex=True)), text)
		print numcheck1
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
def get_pages():
	vapage = wiki.Page('Wikipedia:Vital articles')
	gen = pagegen.links(vapage, ns=0) #we only need mainspace articles
	text = state0 = vapage.get()
	num = 0
	for page in gen:
		text = do_page(page, text)
	wiki.showDiff(state0, text)
	vapage.put(text, 'Bot: Updating Vital Articles')
if __name__ == '__main__':
	wiki.setUser('Legobot')
	get_pages()