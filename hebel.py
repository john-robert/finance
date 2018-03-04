#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
#   Filename:  hebel.py
""" Box of self-written helper functions for Python. """
#   Author:    JRS
#   Date:      Feb 2018
#   License:   GPLv3
#---------------------------------------------------------------------


#---------------------------------------------------------------------
#------------------------ use of: PYTHON 3 ---------------------------
#---------------------------------------------------------------------


###############  python modules import  ##############
import os
import re
import sys
import uuid
import datetime as dt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import newspaper
import fake_useragent
import pandas_datareader.data as web
import pandas as pd
import requests
import csv

######################  functions and classes  ######################
class Logger(object):

	""" 
	Print commands are shown in shell and written to 'logfile'
	at the same time !
	Usage: 
	sys.stdout = Logger(logfile)
	"""

	def __init__(self, logfile):
		self.terminal = sys.stdout
		self.logfile  = logfile
		self.log      = open(self.logfile, "w")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)  

	def flush(self):
		#this flush method is needed for python 3 compatibility.
		#this handles the flush command by doing nothing.
		#you might want to specify some extra behavior here.
		pass 
def make_random_useragent(update_database=False, ua_fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:54.0) Gecko/20100101 Firefox/54.0'):

	"""
	Uses fake_useragent libary from:

	  https://pypi.python.org/pypi/fake-useragent

    - grabs up to date useragent from useragentstring.com
    - randomize with real world statistic via w3schools.com

    ==> Allows to construct strings of "USER_AGENT". These are used
        in html request headers to send basic information 
        (parse engine, browser, OS, ) to web servers.

    If no other user_agent is used, the "request" package via the "torrequest"
    package sends this user agent: python-requests/2.18.1
	"""

	ua_db_file  = './SUP/fake_useragent%s.json' % fake_useragent.VERSION										# when path given, database file is stored and accessed here
	ua          = fake_useragent.UserAgent(path=ua_db_file, fallback=ua_fallback)
	if update_database:
		ua.update()
	return ua.random 																							# random user agent from real world statistic via w3schools.com
def make_uuid(version=4, uuid_base=uuid.NAMESPACE_URL, uuid_string=None):

	"""
	Create universal unique identifier and return it as string.

	Check:
		https://en.wikipedia.org/wiki/Universally_unique_identifier#Versions
		https://docs.python.org/2/library/uuid.html
		https://stackoverflow.com/a/28776880/3429748

	:type version:  int
	:param version: uuid version to be used. check given links for details.

	:type uuid_base:  uuid object
	:param uuid_base: "base uuid" to generate a new uuid when using either version 3 or 5, together with a passed string 'uuid_string'.

	:type uuid_string:  string
	:param uuid_string: String to create a new uuid together with uuid_base for either version 3 or 5.
						Two created uuids with same 'uuid_base' and 'uuid_string' will be identic, so 'uuid_string' should be unique.
	"""


	if version==1:
		uuid = uuid.uuid1()											# uses MAC adress + Datetime

	elif version==3:
		try:
			uuid = uuid.uuid3(uuid_base,uuid_string)				# uses MD5 algorithm for hashing
		except AttributeError:
			uuid = uuid.uuid3(uuid.NAMESPACE_URL,uuid_string)		# uses MD5 algorithm for hashing
			print(u"WARNING:    Uuid namespace (base uuid) is no valid uuid object. Used uuid.NAMESPACE_URL ('6ba7b811-9dad-11d1-80b4-00c04fd430c8') instead.")

	elif version==4:
		uuid = uuid.uuid4()											# uses os random number generator

	elif version==5:
		try:
			uuid = uuid.uuid5(uuid_base,uuid_string)				# uses MD5 algorithm for hashing
		except AttributeError:
			uuid = uuid.uuid5(uuid.NAMESPACE_URL,uuid_string)		# uses MD5 algorithm for hashing
			print(u"WARNING:    Uuid namespace (base uuid) is no valid uuid object. Used uuid.NAMESPACE_URL ('6ba7b811-9dad-11d1-80b4-00c04fd430c8') instead.")

	else:
		print(u'WARNING:    Uuid version %s not valid (only 1, 3, 4, or 5). Used instead version 4 (random number).' % version)
		uuid = uuid.uuid4()

	return str(uuid)


def get_news(hostname_news_page, forget_articles_of_last_time=True, outfile='./LOG/log.txt'):

	"""
	Pass hostname of news paper page. E.g.: "http://www.finanznachrichten.de"
	Print URL, time, title, summary ... into shell and also into outfile (if that is given).
	"""


	# if outfile given (and no error occurs, e.g., directory does not exist ...)
	if outfile:
		sys.stdout = Logger(outfile)												# prints everything into shell but also into the logfile! Basically, I redirected standard out to both. stdout is set to normal at end of script.


	# random user_agent
	user_agent     = make_random_useragent()


	# get news from page
	news_page      = newspaper.build(hostname_news_page, language='de', memoize_articles=forget_articles_of_last_time, fetch_images=False, browser_user_agent=user_agent)
	for article in news_page.articles:

		article.download()															# download article (obviously)
		article.parse()																# parse html to extract meaningful content like authors, body-text, .. (article needs to be downloaded first)
		article.nlp()																# Natural Languange Properties (nlp). Need to call download and parse before ...

		match = re.search(r'(\d{2}.\d{2}.\d{4})\s*.\s*(\d{2}:\d{2})',article.html)	# find often on finanznachrichte.de date/time as: 20.02.2018 / 08:30 (for now does not work for other pages)
		try:
			date                 = match.group(1)
			time                 = match.group(2)
			time_object          = dt.datetime.strptime('%s %s' % (date, time), '%d.%m.%Y %H:%M')
			date_time            = time_object.strftime('%Y-%m-%d, %H:%M Uhr')
		except Exception:
			date_time            = '---'

		print(u'- - - ' * 30)
		print(u'URL:        %s'  % article.url)
		print(u'TIME:       %s'  % date_time)										# not specified by finanznachrichten.de, solved manually
		print(u'TITLE:      %s'  % article.title)
		#print(u'AUTHOR:     %s'  % article.authors)								# not specified by finanznachrichten.de
		#print(u'TEXT:       %s'  % article.text)									# needs parse
		print(u'SUMMARY:    %s'  % article.summary.replace('\n','\n            '))	# needs nlp, replace() is prepend to each new line spaces (just so output is nice)
		print(u'KEYWORDS:   %s'  % ', '.join(article.keywords))						# needs nlp
		print(u'- - - ' * 30)
		print(u'')

	print(u'Finished. Got %s news.' % len(news_page.articles))
	if outfile:
		print(u'Written to: %s' % outfile)
		sys.stdout = sys.__stdout__													# reset stdout to normal 
def get_share_values(ticker, data_source, start, end):

	"""

	"""
def get_google_finance_intraday(ticker, period=60, days=1):
	url = 'https://finance.google.com/finance/getprices?p={}d&f=d,o,h,l,c,v&q={}&i={}'.format(days, ticker, period)
	
	doc = requests.get(url)
	
	data = csv.reader(doc.text.splitlines())
	
	columns = ['Open', 'High', 'Low', 'Close', 'Volume']
	rows = []
	times = []
	for row in data:
	    if re.match('^[a\d]', row[0]):
	        if row[0].startswith('a'):
	            start = datetime.datetime.fromtimestamp(int(row[0][1:]))
	            times.append(start)
	        else:
	            times.append(start+datetime.timedelta(seconds=period*int(row[0])))
	        rows.append(map(float, row[1:]))
	if len(rows):
	    stuff = pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'), columns=columns)
	else:
	    stuff = pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))
	
	print(stuff)


######################  main  ######################
def main():
	argues = sys.argv
	eval(argues[1])


######################  _ _ N A M E _ _ = = " _ _ M A I N _ _ "  ##############
if __name__ == "__main__":
	main()