#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

'''
Individual Wiki Dicts...
Variable being languagecodefamily
'''
enwiki = {
	'baseurl':'http://en.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['enwiki_p','sql-s1'],
	'lang':'en',
	'fam':'wikipedia',
	'namespaces':{
		'-2': 'Media', 
		'-1': 'Special', 
		'0': '', 
		'1': 'Talk', 
		'2': 'User', 
		'3': 'User talk', 
		'4': 'Wikipedia', 
		'5': 'Wikipedia talk', 
		'6': 'File', 
		'7': 'File talk', 
		'8': 'MediaWiki', 
		'9': 'MediaWiki talk', 
		'10': 'Template', 
		'11': 'Template talk', 
		'12': 'Help', 
		'13': 'Help talk', 
		'14': 'Category', 
		'15': 'Category talk', 
		'100': 'Portal', 
		'101': 'Portal talk'
	},
}
frwiki = {
	'baseurl':'http://fr.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['frwiki_p','sql-s3'],
	'lang':'fr',
	'fam':'wikipedia',
	'namespaces': {
		'-2': 'M\u00e9dia', 
		'-1': 'Sp\u00e9cial', 
		'0': '', 
		'1': 'Discussion', 
		'2': 'Utilisateur', 
		'3': 'Discussion utilisateur', 
		'4': 'Wikip\u00e9dia', 
		'5': 'Discussion Wikip\u00e9dia', 
		'6': 'Fichier', 
		'7': 'Discussion fichier', 
		'8': 'MediaWiki', 
		'9': 'Discussion MediaWiki', 
		'10': 'Mod\u00e8le', 
		'11': 'Discussion mod\u00e8le', 
		'12': 'Aide', 
		'13': 'Discussion aide', 
		'14': 'Cat\u00e9gorie', 
		'15': 'Discussion cat\u00e9gorie', 
		'100': 'Portail', 
		'101': 'Discussion Portail', 
		'102': 'Projet', 
		'103': 'Discussion Projet', 
		'104': 'R\u00e9f\u00e9rence', 
		'105': 'Discussion R\u00e9f\u00e9rence'
	}
}
dewiki = {
	'baseurl':'http://de.wikipedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['dewiki_p','sql-s2'],
	'lang':'de',
	'fam':'wikipedia',
	'namespaces': {
		'-2': 'Media', 
		'-1': 'Spezial', 
		'0': '', 
		'1': 'Diskussion', 
		'2': 'Benutzer', 
		'3': 'Benutzer Diskussion', 
		'4': 'Wikipedia', 
		'5': 'Wikipedia Diskussion', 
		'6': 'Datei', 
		'7': 'Datei Diskussion', 
		'8': 'MediaWiki', 
		'9': 'MediaWiki Diskussion', 
		'10': 'Vorlage', 
		'11': 'Vorlage Diskussion', 
		'12': 'Hilfe', 
		'13': 'Hilfe Diskussion', 
		'14': 'Kategorie', 
		'15': 'Kategorie Diskussion', 
		'100': 'Portal', 
		'101': 'Portal Diskussion'
	}

}
commonscommons = {
	'baseurl':'http://commons.wikimedia.org',
	'api':'/w/api.php',
	'index':'/w/index.php',
	'db':['commonswiki_p','sql-s2'],
	'lang':'commons',
	'fam':'commons',
	'namespaces': {
		'-2': 'Media', 
		'-1': 'Special', 
		'0': '', 
		'1': 'Talk', 
		'2': 'User', 
		'3': 'User talk', 
		'4': 'Commons', 
		'5': 'Commons talk', 
		'6': 'File', 
		'7': 'File talk', 
		'8': 'MediaWiki', 
		'9': 'MediaWiki talk', 
		'10': 'Template', 
		'11': 'Template talk', 
		'12': 'Help', 
		'13': 'Help talk', 
		'14': 'Category', 
		'15': 'Category talk', 
		'100': 'Creator', 
		'101': 'Creator talk'
	}
}
lyricwiki = {
	'baseurl':'http://lyricwiki.org',
	'api':'/mw_api.php',
	'index':'',
	'db':None,
	'lang':'en',
	'fam':'LyricWiki',
	'namespaces': {
		'-2': 'Media', 
		'-1': 'Special', 
		'0': '', 
		'1': 'Talk', 
		'2': 'User', 
		'3': 'User talk', 
		'4': 'LyricWiki', 
		'5': 'LyricWiki talk', 
		'6': 'File', 
		'7': 'File talk', 
		'8': 'MediaWiki', 
		'9': 'MediaWiki talk', 
		'10': 'Template', 
		'11': 'Template talk', 
		'12': 'Help', 
		'13': 'Help talk', 
		'14': 'Category', 
		'15': 'Category talk'
	}
}
'''
Main wikilist used by PythonWikiBot
URL is key, Wiki Dict above is given
'''
wikilist = {
	'en.wikipedia.org': enwiki,
	'fr.wikipedia.org': frwiki,
	'de.wikipedia.org': dewiki,
	'commons.wikimedia.org':commonscommons,
	'lyricwiki.org':lyricwiki,
}
