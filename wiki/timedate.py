#!usr/bin/python
import time, datetime
"""
Not to be run as a file
Contains lists and dictionaries to help with dates
Only for English Language, however translations are welcome.
"""
MonthNames    = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]

def monthname(number):
	"""
	Returns the month name
	for the given integer.
	"""
	return MonthNames[int(number)-1]


days_in_month = {
	1:  31,
	2:  29,
	3:  31,
	4:  30,
	5:  31,
	6:  30,
	7:  31,
	8:  31,
	9:  30,
	10: 31,
	11: 30,
	12: 31
}
num_to_month = {
	1:'January',
	2:'February',
	3:'March',
	4:'April',
	5:'May',
	6:'June',
	7:'July',
	8:'August',
	9:'September',
	10:'October',
	11:'November',
	12:'December',
}
month_to_num = {
'January': 1,
'February': 2,
'March': 3,
'April': 4,
'May': 5,
'June': 6,
'July': 7,
'August': 8,
'September': 9,
'October': 10,
'November': 11,
'December': 12,
}

def daysinmonth(var):
	"""
	Returns the number of days in a month.
	var = month name or number
	"""
	try:
		int(var)
		num = True
	except ValueError:
		num = False
	if num:
		return days_in_month[int(var)]
	number = month_to_num[var]
	return days_in_month[number]
def currtime():
	"""
	Returns a time.time() object
	"""
	return time.time()
def currentmonth():
	"""
	Returns the integer of the current month.
	To get the current month name, use monthname(currentmonth())
	"""
	return time.gmtime(currtime()).tm_mon
def currentyear():
	return time.gmtime(currtime()).tm_year
def numwithzero(num):
	"""
	Returns a str where their is a
	'0' in front of a number
	"""
	num = int(num)
	if num >= 10:
		return str(num)
	else:
		return '0%' + str(num)
def monthname(num):
	"""
	Returns the name of the month based on the integer.
	"""
	return num_to_month[int(num)]

def convertts(ts):
	"""
	Converts MediaWiki timestamps (ISO 8601)
	to a human readable one.
	"""
	epochts = int(time.mktime(time.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')))
	st = time.gmtime(epochts)
	year = str(st.tm_year)
	hour = str(st.tm_hour)
	min = str(st.tm_min)
	monthname1 = monthname(st.tm_mon)
	day = str(st.tm_mday)
	return '%s:%s, %s %s %s' %(hour, min, day, monthname1, year)
