#!usr/bin/python
import wiki
from wiki import pagegen, timedate
import re, time, sys
wiki.setUser('Legobot III')
#get the list of protection templates...
fulllist = []
gen = pagegen.category(wiki.Page('Category:Protection templates'))
for page in gen:
	if page.isTemplate():
		name = page.titlewonamespace()
		fulllist.append(name)

moveprot = ['pp-move-dispute','pp-move-vandalism','pp-move-indef','pp-move']
def logerror(page):
	try:
		orig = open('Errors.txt', 'r')
		content = orig.read()
		orig.close()
	except:
		content = ''
	new = open('Errors.txt', 'w')
	new.write(content + '\n' + page.title())
	print 'Logging an error on ' + page.title()
	new.close()

def convertexpiry(ts):
	epochts = int(time.mktime(time.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')))
	st = time.gmtime(epochts)
	year = str(st.tm_year)
	monthname = timedate.monthname(st.tm_month)
	day = str(st.tm_mday)
	return '%s %s, %s' %(monthname, day, year)		
		
def dopage(page): #old way, fixing now
    wikitext = state0 = page.get()
    protlevel = page.protectlevel()
    print protlevel
    if len(protlevel.keys()) == 0:
		for template in fulllist:
			wikitext = removetemplate(wikitext, template)
	if protlevel.has_key('edit'):
		if protlevel['edit']['level'] == 'sysop':
			return 'Prot'
    if protlevel.has_key('edit') and protlevel.has_key('move'):
		if (protlevel['move']['expiry'] == 'infinity') and (protlevel['move']['level'] == 'autoconfirmed'):
			for template in moveprot:
				wikitext = removetemplate(wikitext, template)
    if protlevel.has_key('move'):
		move = protlevel['move']
		if (move['level'] == 'sysop') and (move['expiry'] == 'infinity'):
			if not ('{{pp-move' in wikitext.lower()):
				wikitext = '{{pp-move-indef}}\n' + wikitext
    if ('{{pp-semi' in wikitext.lower()) and (protlevel.has_key('edit') == False):
        wikitext = removetemplate(wikitext, 'pp-semi-protected')
        wikitext = removetemplate(wikitext, 'pp-semi-vandalism')
        wikitext = removetemplate(wikitext, 'pp-semi')
        wikitext = removetemplate(wikitext, 'pp-semi-indef')
    if ('{{pp-dispute' in wikitext.lower()):
        if protlevel.has_key('edit'):
            if protlevel['edit']['level'] != 'sysop':
                wikitext = removetemplate(wikitext, 'pp-dispute')
        else:
            wikitext = removetemplate(wikitext, 'pp-dispute')
    if wikitext != state0:
		try:
			wiki.showDiff(state0,wikitext)
			page.put(wikitext, 'Bot: Maintaining protection tags', bot=True)
			return True
		except wiki.LockedPage:
			print 'Skipping %s due to full protection' %page.title()
			return 'Prot'
    else:
        print 'Not making any changes???'
        return False

def removetemplate(wikitext, template):
	wikitext = re.compile(r'\{\{\s*%s((.*?)|)\}\}' %template, re.IGNORECASE).sub(r'', wikitext)
	return wikitext
def checktalk():
	page = wiki.Page('User:Legobot III/Stop')
	try:
		text = page.get()
		if text.lower() != 'run':
			sys.exit('Run page disabled')
	except:
		sys.exit('Run page disabled')
	
def main():
	gen = pagegen.category(wiki.Page('Category:Wikipedia pages with incorrect protection templates'))
	for page in gen:
		checktalk()
		print page.title() +' is being processed.'
		if page.namespace() in [2, 3, 10]:
			print 'Skipping userspace/template pages.'
		else:
			y=dopage(page)
			if y == 'Prot':
				logerror(page)
if __name__ == '__main__':
	main()