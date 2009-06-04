#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
This script is a clone of [[en:User:SmackBot]]
Syntax: python datebot.py
"""

#
# (C) Legoktm 2008-2009, MIT License
# 
__version__ = '$Id$'
import re, sys, time
import os
import wiki
from wiki import pagegen, config, timedate

# Define global constants
readDelay  = 20	# seconds
writeDelay = 60 # seconds
usernames = {
	'en.wikipedia.org':'Legobot II',
}
wiki.setUser(usernames[config.wiki])
def checktalk():
	page = wiki.Page('User:%s/Stop' %(usernames[config.wiki]))
	try:
		wikitext = page.get()
	except:
		sys.exit()
	if wikitext.lower() != 'run':
		sys.exit()
def process_article(page):
	month_name = timedate.monthname(timedate.currentmonth())
	year = timedate.currentyear()
	try:
		wikitext = state1 = page.get()
	except wiki.IsRedirectPage:
		return
	# Fix Casing (Reduces the number of possible expressions)
	wikitext = re.compile(r'\{\{\s*(template:|)fact', re.IGNORECASE).sub(r'{{Fact', wikitext)
	# Fix some redirects
	wikitext = re.compile(r'\{\{\s*(template:|)cn\}\}', re.IGNORECASE).sub(r'{{Fact}}', wikitext)
	wikitext = re.compile(r'\{\{\s*(template:|)citation needed', re.IGNORECASE).sub(r'{{Fact', wikitext)
	wikitext = re.compile(r'\{\{\s*(template:|)proveit', re.IGNORECASE).sub(r'{{Fact', wikitext)
	wikitext = re.compile(r'\{\{\s*(template:|)sourceme', re.IGNORECASE).sub(r'{{Fact', wikitext)
	wikitext = re.compile(r'\{\{\s*(template:|)fct', re.IGNORECASE).sub(r'{{Fact', wikitext)
	# State point.  Count any changes as needing an update if they're after this line
	state0 = wikitext
	
	# Date the tags
	wikitext = re.compile(r'\{\{\s*fact\}\}', re.IGNORECASE).sub(r'{{Fact|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*wikify\}\}', re.IGNORECASE).sub(r'{{Wikify|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*orphan\}\}', re.IGNORECASE).sub(r'{{Orphan|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*uncategorized\}\}', re.IGNORECASE).sub(r'{{Uncategorized|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*uncatstub\}\}', re.IGNORECASE).sub(r'{{Uncatstub|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*cleanup\}\}', re.IGNORECASE).sub(r'{{Cleanup|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*unreferenced\}\}', re.IGNORECASE).sub(r'{{Unreferenced|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*importance\}\}', re.IGNORECASE).sub(r'{{importance|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*Expand\}\}', re.IGNORECASE).sub(r'{{Expand|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
#	wikitext = re.compile(r'\{\{\s*merge(.*?)\}\}', re.IGNORECASE).sub(r'{{Merge\\1|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*copyedit\}\}', re.IGNORECASE).sub(r'{{Copyedit|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*refimprove\}\}', re.IGNORECASE).sub(r'{{Refimprove|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = re.compile(r'\{\{\s*primary sources\}\}', re.IGNORECASE).sub(r'{{Primary sources|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}', wikitext)
	wikitext = wikitext.replace('{{subst:CURRENTMONTHNAME}}', month_name)
	wikitext = wikitext.replace('{{subst:CURRENTYEAR}}', year)
	EditMsg = "Date maintenance tags"
	if state1 != state0:
		EditMsg = EditMsg + " and general fixes"
	# If the text has changed at all since the state point, upload it
	if wikitext != state0:
		print 'Editing ' + page.title()
		print 'WRITE:	Adding %s bytes.' % str(len(wikitext)-len(state0))
		try:
			page.put(wikitext, EditMsg, bot=True)
		except wiki.LockedPage:
			print 'SKIP: ' + page.title() + ' is locked.'
#		except KeyboardInterrupt:
#			quit()
#		except:
#			print 'ERROR:	Except raised while writing.'
	else:
		print 'Skipping ' + page.title() + ' due to no changes made after state point.'
def docat(cat2):
	gen = pagegen.category(wiki.Page('Category:' + cat2))
	for page in gen:
		if page.namespace() == 0:
			try:
				process_article(page)
			except UnicodeEncodeError:
				pass
			checktalk()
		else:
			print 'Skipping %s because it is not in the mainspace' %(page.title())
	print 'Done with Category:%s' %(cat2)
def main():
	docat("Articles with unsourced statements")
	docat("Articles that need to be wikified")
	docat("Orphaned articles")
	docat("Category needed")
	docat("Uncategorized stubs")
	docat("Wikipedia cleanup")
	docat("Articles lacking sources")
	docat("Articles to be expanded")
	docat("Articles with topics of unclear notability")
#	docat("Articles to be merged")
	docat("Wikipedia articles needing copy edit")
	docat("Articles needing additional references")
	docat("Articles lacking reliable references")
	print 'Done'
	
if __name__ == "__main__":
	wiki.getArgs() #so that we get the site...
	while True:
		main()
		print 'Sleeping 600 seconds'
		time.sleep(600)
