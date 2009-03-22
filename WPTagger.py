#!usr/bin/python
#-*- coding:utf-8 -*-
#
# (C) Legotkm 2009 MIT License
#
"""
Tags talk pages for a wikiproject
Syntax Example: python WPTagger.py "{{WikiProject Piracy}}" "[[WP:WikiProject Piracy]]" -cat:Category:Piracy
"""
from pywikibot import wiki, pagegen
wiki.setUser('Legobot')
import time, re
def doProject(tag, projname, gen):
	tag1 = tag
	rds = wiki.Page(tag).redirects()
	rds1 = []
	for page in rds:
		rds1.append('{{' + page.titlewonamespace())
	list = []
	for page in gen:
		print page.title()
		try:
			dopage(page, tag1, rds1, projname)
		except UnicodeDecodeError:
			print 'Skipping %s because of UnicodeDecodeError.' %page.title()
		time.sleep(2.5)

def dopage(page, tag, rds, projname):
	if not page.isTalk():
		page = page.toggletalk()
	realtag = tag
	summary = 'Bot: Tagging for %s with %s' %(projname, tag)
	if page.toggletalk().isRedirect():
		print page.title() + ' is a redirect, skipping.'
		return
	if page.exists():
		print page.title() + ' exists.'
		try:
			wikitext = page.get()
		except wiki.IsRedirectPage:
			return
	else:
		print page.title() + ' doesn\'t exist.'
		page.put(tag, summary)
		return
	regex = tag.replace('_',' ')
	if regex.lower() in wikitext.lower().replace('_',' '):
		print page.title() + ' has template1 found passing.'
		return
	if rds:
		for tag in rds:
			regex = tag.split('}')[0].split('|')[0]
			if tag.lower() in wikitext.lower().replace('_',' '):
				print page.title() + ' has %s found passing.' %tag
				return
	#hasnt been found
	print page.title() + ' doesn\'t have the template.'	
	#check for WPBanner Shell
	if re.search('\{\{WikiProjectBannerShell(\s|)(|\n)(|\s)\|1\=', wikitext, re.I):
		newtext = re.sub('\{\{WikiProjectBannerShell(\s|)(|\n)(|\s)\|1\=','{{WikiProjectBannerShell|1=\n%s' % realtag, wikitext, re.I)
	else:
		newtext = realtag + '\n' + wikitext #just add on top
	wiki.showDiff(wikitext, newtext)
	page.put(newtext, summary)
		
def main():
	args = wiki.getArgs()
	tag = args[0]
	print tag
	projname = args[1]
	print projname
	gen = pagegen.handleArgs()
	doProject(tag, projname, gen)
if __name__ == '__main__':
	main()