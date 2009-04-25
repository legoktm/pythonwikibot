#!usr/bin/python
import re
from pywikibot import wiki, pagegen
wiki.setUser('Legobot')
__version__ = '$Id$'
def main():
	gen = pagegen.category(wiki.Page('Category:WikiProject Korea articles using the wg parameter'))
	for page in gen:
		do_page(page)

def do_page(page):
	try:
		print unicode(page)
		wikitext = page.get()
	except UnicodeEncodeError:
		return
	#fix all of the wg= parameters
	newtext = re.compile('wg=architect', re.IGNORECASE).sub('architecture=yes', wikitext)
	newtext = re.compile('wg=architecture', re.IGNORECASE).sub('architecture=yes', newtext)
	newtext = re.compile('wg=arts', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=art', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=painting', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=music', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=dance', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=literature', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=poetry', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=pottery', re.IGNORECASE).sub('arts=yes', newtext)
	newtext = re.compile('wg=baseball', re.IGNORECASE).sub('baseball=yes', newtext)
	newtext = re.compile('wg=base', re.IGNORECASE).sub('baseball=yes', newtext)
	newtext = re.compile('wg=cuisine', re.IGNORECASE).sub('cuisine=yes', newtext)
	newtext = re.compile('wg=food', re.IGNORECASE).sub('cuisine=yes', newtext)
	newtext = re.compile('wg=film', re.IGNORECASE).sub('film=yes', newtext)
	newtext = re.compile('wg=movie', re.IGNORECASE).sub('film=yes', newtext)
	newtext = re.compile('wg=cinema', re.IGNORECASE).sub('film=yes', newtext)
	newtext = re.compile('wg=history', re.IGNORECASE).sub('history=yes', newtext)
	newtext = re.compile('wg=hist', re.IGNORECASE).sub('history=yes', newtext)
	newtext = re.compile('wg=housekeeping', re.IGNORECASE).sub('housekeeping=yes', newtext)
	newtext = re.compile('wg=hk', re.IGNORECASE).sub('housekeeping=yes', newtext)
	newtext = re.compile('wg=milhist', re.IGNORECASE).sub('milhist=yes', newtext)
	newtext = re.compile('wg=military', re.IGNORECASE).sub('milhist=yes', newtext)
	newtext = re.compile('wg=mh', re.IGNORECASE).sub('milhist=yes', newtext)
	newtext = re.compile('wg=military history', re.IGNORECASE).sub('milhist=yes', newtext)
	newtext = re.compile('wg=nk', re.IGNORECASE).sub('nk=yes', newtext)
	newtext = re.compile('wg=dprk', re.IGNORECASE).sub('nk=yes', newtext)
	newtext = re.compile('wg=north korea', re.IGNORECASE).sub('nk=yes', newtext)
	newtext = re.compile('wg=pop', re.IGNORECASE).sub('pop=yes', newtext)
	newtext = re.compile('wg=popcult', re.IGNORECASE).sub('pop=yes', newtext)
	newtext = re.compile('wg=popculture', re.IGNORECASE).sub('pop=yes', newtext)
	newtext = re.compile('wg=popular culture', re.IGNORECASE).sub('pop=yes', newtext)
	newtext = re.compile('wg=skgeo', re.IGNORECASE).sub('skgeo=yes', newtext)
	newtext = re.compile('wg=skg', re.IGNORECASE).sub('skgeo=yes', newtext)
	newtext = re.compile('wg=skg culture', re.IGNORECASE).sub('skgeo=yes', newtext)
	newtext = re.compile('wg=skcc', re.IGNORECASE).sub('skgeo=yes', newtext)
	newtext = re.compile('wg=south korean geography', re.IGNORECASE).sub('skgeo=yes', newtext)
	#fix the templated redirects
	newtext = re.sub('\{\{[Kk]orean','{{WikiProject Korea', newtext)
	newtext = re.sub('\{\{[Ww]PKorea','{{WikiProject Korea', newtext)
	newtext = re.sub('\{\{[Ww]PKOREA','{{WikiProject Korea', newtext)
	wiki.showDiff(wikitext, newtext)
	page.put(newtext, 'Bot: fixing depreacted wg parameter [[WP:BOTR#.7B.7BWikiProject_Korea.7D.7D_cleanup|per request]]')

if __name__ == '__main__':
	main()