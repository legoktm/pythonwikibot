#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

"""
Individual Wiki Dicts...
Variable being languagecodefamily
"""
enwiki = {
	'baseurl':'http://en.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['enwiki_p','sql-s1'],
	'lang':'en',
	'fam':'wikipedia',
}
frwiki = {
	'baseurl':'http://fr.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['frwiki_p','sql-s3'],
	'lang':'fr',
	'fam':'wikipedia',
}
dewiki = {
	'baseurl':'http://de.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['dewiki_p','sql-s2'],
	'lang':'de',
	'fam':'wikipedia',
}
commonscommons = {
	'baseurl':'http://commons.wikimedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['commonswiki_p','sql-s2'],
	'lang':'commons',
	'fam':'commons',
}
lyricwiki = {
	'baseurl':'http://lyricwiki.org',
	'api':'mw_api.php',
	'index':'',
	'db':None,
	'lang':'en',
	'fam':'LyricWiki'
}
"""
Main wikilist used by PythonWikiBot
URL is key, Wiki Dict above is given
"""
wikilist = {
	'en.wikipedia.org': enwiki,
	'fr.wikipedia.org': frwiki,
	'de.wikipedia.org': dewiki,
	'commons.wikimedia.org':commonscommons,
	'lyricwiki.org':lyricwiki,
}