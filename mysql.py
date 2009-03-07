#!usr/bin/python
import sys
import config, wiki
if config.ts:
	TSUser = config.ts
else:
	raise wiki.NoTSUsername('No Toolserver username given.')
"""
Script that has MySQL Functions for toolserver users
Wiki should be in the form of langproject (ex. enwiki) without the '_p' on the end
Host is either 1, 2, or 3.  Can be left blank
"""


class MySQL:
	
	def __init__(self, username = False):
		try:
			import MySQLdb
		except ImportError:
			raise wiki.MySQLError('MySQLdb not installed.  MySQL class cannot be used')
		if not username:
			self.user = TSUser
		else:
			self.user = username
	def query(self, q, db, host=False):
		if (db != 'toolserver') and (not ('_p' in db)):
			db += '_p'
		if not host:
			host = self.gethost(db)
		elif host != 'sql':
			host = 'sql-s' + str(host)	
		self.conn = MySQLdb.connect(db=db, host=host, read_default_file="/home/%s/.my.cnf" %(self.user))
		self.cur = self.conn.cursor()
		self.cur.execute(q)
		self.res = self.cur.fetchall()
		self.cur.close()
		return res
	def gethost(self, db):
		res = self.query(q="SELECT server FROM wiki WHERE dbname = '%s';" %(db), db='toolserver', host='sql')
		try:
			return res[0][0]
		except IndexError:
			raise wiki.MySQLError('%s does not exist.' %db)

trySQL = MySQL()
def editcount(user, db):
	res = SQL.query("SELECT user_editcount FROM user WHERE user_name = '%s';" %(user), db)
	try:
		return res[0][0]
	except IndexError:
		raise NoUsername('%s doesnt exist on %s' %(user, db))