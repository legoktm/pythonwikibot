#!usr/bin/python
import time
"""
Not to be run as a file
Contains lists and dictionaries to help with dates
Only for English Language
"""
MonthNames    = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]

def monthname(number):
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
	return time.time()
def numwithzero(num):
	num = int(num)
	if num >= 10:
		return str(num)
	else:
		return '0%' + str(num)
def monthname(num):
	return num_to_month[int(num)]

def convertts(ts):
	epochts = int(time.mktime(time.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')))
	st = time.gmtime(epochts)
	year = str(st.tm_year)
	hour = str(st.tm_hour)
	min = str(st.tm_min)
	monthname1 = monthname(st.tm_mon)
	day = str(st.tm_mday)
	return '%s:%s, %s %s %s' %(hour, min, day, monthname1, year)