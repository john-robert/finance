#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
#   Filename:  hebel.py
""" Box of self-written helper functions for Python. """
#   Author:    John - Robert Scholz
#   Date:      Feb 2018
#   Email:     john.robert.scholz@gmail.com
#   License:   GPLv3
#---------------------------------------------------------------------


#---------------------------------------------------------------------
#---------------------- use of: PYTHON 3 -----------------------------
#---------------------------------------------------------------------


###############  python modules import  ##############
import os
import re
import sys
import glob
import time
import shutil
import datetime
import math as M
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import newspaper
import fake_useragent


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
def make_random_user_agent(update_database=False):

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

	ua_db_file  = 'fake_useragent%s.json' % fake_useragent.VERSION														# when path given, database file is stored and accessed here
	ua_fallback = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:54.0) Gecko/20100101 Firefox/54.0' 					# case of any exceptions/failures use this. from Mac OS X, Firefox
	ua          = fake_useragent.UserAgent(path=ua_db_file, fallback=ua_fallback)
	if update_database:
		ua.update()
	return ua.random 																									# random user agent from real world statistic via w3schools.com
def get_news(hostname_news_page, forget_articles_of_last_time=True, outfile=None):

	"""
	Pass hostname of news paper page. E.g.: "http://www.finanznachrichten.de"
	Print URL, time, title, summary ... into shell and also into outfile (if that is given).
	"""


	# if outfile given (and no error occurs, e.g., directory does not exist ...)
	if outfile:
		sys.stdout = Logger(outfile)												# prints everything into shell but also into the logfile! Basically, I redirected standard out to both. stdout is set to normal at end of script.


	# random user_agent
	user_agent     = make_random_user_agent()


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
			time_object          = datetime.datetime.strptime('%s %s' % (date, time), '%d.%m.%Y %H:%M')
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
		print(u'Written to:\n%s' % outfile)
		sys.stdout = sys.__stdout__													# reset stdout to normal 



######################  main  ######################
def main():
	argues = sys.argv
	eval(argues[1])


######################  _ _ N A M E _ _ = = " _ _ M A I N _ _ "  ##############
if __name__ == "__main__":
	main()
