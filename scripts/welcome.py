#!usr/bin/python
import wiki
from wiki import userlib
import re, time, sys
reload(sys)
sys.setdefaultencoding('utf-8')

logs = {
	'en':None,
	'commons': 'Project:Welcome log',
}
templates = {
	'en':'{{subst:welcome}} ~~~~',
	'commons': '{{subst:welcome}} ~~~~',
}
logupmess = {
	'en':None,
	'commons': 'Bot: Updating log',
}
welcomemess = {
	'en':'Welcome!',
	'commons': 'Welcome!',
}
class WelcomeBot:
		def __init__(self):
			print 'Initializing...'
			#---------------------------------------------#
			#-------------SETTINGS START HERE-------------#
			#---------------------------------------------#
			self.editcount = 0						#Must have at least this many edits
			self.loadusers = 5000					#How many users to load
			self.waittime = 30						#How many seconds to wait after each run
			self.quitafterrun = False				#Whether to quit after running
			#---------------------------------------------#
			#--------------SETTINGS END HERE--------------#
			#----------DO NOT TOUCH BELOW THIS LINE-------#
			#---------------------------------------------#
			self.welcomemess = wiki.translate(welcomemess)
			self.template = wiki.translate(templates)
			self.logupmess = wiki.translate(logupmess)
		def run(self):
			url = wiki.getWiki().getIndex() + '?title=Special:Log/newusers&limit=' + str(self.loadusers)
			text = wiki.getURL(url)
			rec = '\<a href="/w/index\.php\?title=User:(.*?)&amp;action=edit&amp;redlink=1"'
			list = re.findall(rec, text)
			userlist = []
			for i in list:
				userlist.append(userlib.User(wiki.Page('User:'+i)))
			logpost = ''
			for user in userlist:
				logpost += self.doUser(user)
				time.sleep(2)
			self.updatelog(logpost)
			if not self.quitafterrun:
				print 'Sleeping %s' %self.waittime
				time.sleep(self.waittime)
				bot = WelcomeBot()
				bot.run()
			else:
				sys.exit()
		def doUser(self, user):
			try:
				usereditcount = user.editcount()
			except ValueError,e:
				return ''
			if usereditcount < self.editcount:
				print '%s doesn\'t have enough edits to be welcomed.' %user.name()
				return ''
			if user.isBlocked():
				print '%s is blocked.' %user.name()			
				return '' 
			if user.Page().toggletalk().exists():
				print '%s already has a talk page.' %user.name()
				return ''
			talkpage = user.Page().toggletalk()
			print 'Welcoming %s.' %user.name()			
			talkpage.put(self.template, self.welcomemess)
			return '\n{{WLE|user=%s|contribs=%s}}' %(user.name(), usereditcount)
		def updatelog(self, text):
			rightime = time.localtime(time.time())
			year = str(rightime[0])
			month = str(rightime[1])
			day = str(rightime[2])
			if len(month) == 1:
				month = u'0' + month
			try:
				self.log = logs[wiki.translate()]
			except KeyError: #no log on wiki
				return
			if not self.log:
				return
			target = self.log + '/' + year + '/' + month + '/' + day
			log = wiki.Page(target)
			if not log.exists():
				text = '{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"\n!User\n!Contribs\n' + text
			log.put(text, self.logupmess)

if __name__ == '__main__':
	bot = WelcomeBot()
	bot.run()
