#!usr/bin/python
import wiki, pagegen
import re, time
def dopage(page):
	wikitext = state = page.get()
	if 'reflist' in wikitext:
		print 'It already has template'
		return
	elif 'references' in wikitext:
		print 'It already has template'
		return
	wikitext = re.compile(r'\n== External links ==', re.IGNORECASE).sub(r'\n== References ==\n{{reflist}}\n== External links ==', wikitext)
	wiki.showDiff(state, wikitext)
	page.put(wikitext, 'Bot: Adding {{reflist}} tag')

def main():
	gen = pagegen.category(wiki.Page('Category:Wikipedia pages with broken references'))
	for page in gen:
		print page
		dopage(page)
		time.sleep(15)

if __name__ == "__main__":
	main()