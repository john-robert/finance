#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
""" Box of self-written helper functions for Python3. """
#   Date:      Feb 2018
#   License:   GPLv3
#---------------------------------------------------------------------


###############  INITIATION  ##############
__title__ = 'kampfname'
__author__ = 'John-Robert Scholz'


###############  PYTHON  MODULES  IMPORT  ##############
# Python standard libaries
import os
import re
import sys
import uuid
import time
import pickle
import threading
import datetime as dt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
#import multiprocessing

# private libary
#from email_custom import Email

# libaries that need extra installation (e.g. via conda, pip, or direct from source code)
import newspaper
import fake_useragent
import dateutil as du
import matplotlib.pyplot as plt
import alpha_vantage.timeseries as ts
import pandas as pd
pd.set_option('display.width', 100)


######################  classes & classes  ######################
###  classes  ###
class Logger:

	""" 
	Print commands are shown in shell and written to 'logfile'
	at the same time !
	Usage: 
	sys.stdout = Logger(logfile)
	"""

	def __init__(self, logfile):
		self.terminal = sys.stdout
		self.logfile  = logfile
		self.log      = open(self.logfile, "a")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)  

	def flush(self):
		#this flush method is needed for python 3 compatibility.
		#this handles the flush command by doing nothing.
		#you might want to specify some extra behavior here.
		pass 
class BetterArticle:

	"""

	"""


	def __init__(self, article, *args, **kwargs):

		article.build()

		match                  = re.search(r'(\d{2}.\d{2}.\d{4})\s*.\s*(\d{2}:\d{2})', article.html)
		if match:
			date_str           = match.group(1)
			time_str           = match.group(2)
			time_object        = dt.datetime.strptime('%s %s' % (date_str, time_str), '%d.%m.%Y %H:%M') 
			date_time_pretty   = time_object.strftime('%Y-%m-%d, %H:%M Uhr') + '(UTC %+dh)' % int(-time.timezone/3600)
			self.is_datetime   = True
		else:
			date_time_pretty   = "---"
			self.is_datetime   = False

		self.html              = article.html
		self.url               = article.url
		self.date_time_pretty  = date_time_pretty
		self.publish_date      = article.publish_date
		self.title             = article.title
		self.authors           = article.authors									# not specified by finanznachrichten.de
		self.text              = article.text										# needs parse
		self.summary           = article.summary									# needs nlp
		self.keywords          = article.keywords									# needs nlp
 
		self.uuid_hash         = make_uuid_hash(variant=5, uuid_base=uuid.NAMESPACE_URL, uuid_string=self.url)
		self.related_companies, self.related_stocks = self._related_stocks()
		self.auto_weight       = self._auto_weight()
		self.manu_weight       = None


	def __str__(self):
		string_representation = u'\n'                \
								u'{}\n'              \
								u'URL:         {}\n' \
								u'TIME:        {}\n' \
								u'UUID:        {}\n' \
								u'TITLE:       {}\n' \
								u'AUTHOR:      {}\n' \
								u'PUB DATE:    {}\n' \
								u'SUMMARY:     {}\n' \
								u'KEYWORDS:    {}\n' \
								u'{}\n'.format(u'- - - ' * 30, self.url, self.date_time_pretty, self.uuid_hash, self.title, self.authors, self.publish_date, self.summary.replace('\n','\n             '), ', '.join(self.keywords), u'- - - ' * 30, )
								 #print(u'TEXT:        %s'  % self.text)
								 #print(u'COMPANIES:   %s'  % ', '.join(self.related_companies))
								 #print(u'REL_TICKER:  %s'  % ', '.join(self.related_stocks))

		return string_representation


	def _related_stocks(self):
		csv_ticker             = pd.read_csv('./INFO/ticker_symbols/XETRA.csv', sep=';')
		related_companies      = []
		related_stocks         = []

		for keyword in self.keywords:			# muss noch verbessert werdeb
			keyword            = keyword.upper()
			match              = csv_ticker[ csv_ticker['Company'].str.contains(keyword) ]
			related_companies += list( match['Company'] )
			related_stocks    += list( match['Symbol'] )

		return list(set(related_companies)), list(set(related_stocks))


	def _auto_weight(self):
		# Google AI
		return 0


	def _manu_weight(self):
		self.show()
		weight                = input('How do you think this news impacts the related stock(s):  [-3, -2, -1, 0, 1, 2, 3]:\t')
		return weight


	def store(self):
		article_path = os.path.join('./NEWS', self.uuid_hash)
		pickle.dump(self, open(article_path, 'wb'))
		print(u'Article stored: %s' % article_path)


	def reassign_related_stocks(self):
		self.related_companies, self.related_stocks = self._related_stocks()


	def redo_auto_weight(self):
		self.auto_weight      = _auto_weight()


	def set_manu_weight(self, weight):
		self.manu_weight      = weight


	def show(self):
		print(self)


	def save(self, outfile='./LOG/log.txt'):
		with open(outfile, "a") as fp:
			pass
			#fp.write(self.title)
class Equity:

	"""


	"""

	def __init__(self, ticker='MSFT', start=None, end=None, alpha_vantage_APIkey='7NSGBW8REI0PSVAC'):

		self.ticker              = ticker
		self.plot_filename       = None

		# handel start and end date of request
		self.retrieve_day        = dt.datetime.today()
		if start:
			self.start           = du.parser.parse(start)
		else:
			self.start           = self.retrieve_day-dt.timedelta(days=1000)
		if end:
			self.end             = du.parser.parse(end)
		else:
			self.end             = self.retrieve_day
		if self.start > self.end:
			self.start, self.end = self.end, self.start
		if self.start >= self.retrieve_day-dt.timedelta(days=140) and self.end >= self.retrieve_day-dt.timedelta(days=140):
			outputsize = 'compact'
		else:
			outputsize = 'full'

		# get data according to specified times
		timeseries               = ts.TimeSeries(key=alpha_vantage_APIkey, output_format='pandas')
		self.data, self.metadata = timeseries.get_daily(symbol=self.ticker, outputsize=outputsize)
		self.data.Date           = pd.to_datetime(self.data.index, format='%Y-%m-%d')
		self.data.set_index(self.data.Date, inplace=True)
		self.data                = self.data[self.start:self.end]


	def __str__(self):
		return '%s (from: %s to: %s)' % (self.ticker, self.data.index[0].strftime("%Y-%m-%d"), self.data.index[-1].strftime("%Y-%m-%d"))


	def first(self, n=1):
		return self.data.iloc[:n,:]


	def last(self, n=1):
		return self.data.iloc[-n:,:]


	def update(self):
		self.data                = self.data


	def plot(self, columns='1. open', kind='line', show=True, plot_filename=None):

		"""
		columns: default: '1. open'. Or choose e.g.: ['1. open, '2. high', '3. low', '4. close', '5. volume']. Or: columns=list(self.data.columns.values)[:-1]
		kind: 'line', 'bar', 'barh', 'scatter', ... Check: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html
		"""

		fig = plt.figure(num=None, figsize=(14, 10), dpi=80, facecolor='w', edgecolor='k')
		ax  = fig.add_subplot(111)
		ax.grid(ls='-.', lw=1)
		ax.legend(loc='upper left', fontsize=10)
		ax.tick_params(axis='both', which='major', labelsize=10)
		ax.tick_params(axis='both', which='minor', labelsize=9)
		ax.set_xlabel('Dates (%s trading days)' % len(self.data), fontsize=12)
		ax.set_ylabel('Equity value', fontsize=12)
		ax.set_title('%s' % self.__str__(), fontsize=14)
		self.data.plot(y=columns, kind=kind, ax=ax, lw=2)
		fig.tight_layout()

		if show:
			plt.show()

		if plot_filename:
			self.plot_filename = os.path.join('./PLOTS', plot_filename)
			plt.savefig(self.plot_filename)
			print(u'Equity plot stored:\n%s' % self.plot_filename)
def random_useragent(update_database=False, ua_fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:54.0) Gecko/20100101 Firefox/54.0'): 

		"""
		Uses fake_useragent libary from:
	
		  https://pypi.python.org/pypi/fake-useragent
	
		- grabs up to date useragent from useragentstring.com
		- randomize with real world statistic via w3schools.com
	
			==> Allows to construct strings of "USER_AGENT". These are used
			in html request headers to send basic information 
			(parse engine, browser, OS, ) to web servers.
		"""


		ua_db_file  = './INFO/fake_useragent%s.json' % fake_useragent.VERSION
		ua          = fake_useragent.UserAgent(path=ua_db_file, fallback=ua_fallback)	# when path given, database file is stored and accessed here
		if update_database:
			ua.update()
		return ua.random 														# random user agent from real world statistic via w3schools.com
def make_uuid_hash(variant=4, uuid_base=uuid.NAMESPACE_URL, uuid_string=None):

	"""
	Create universal unique identifier and return it as string.

	Check:
		https://en.wikipedia.org/wiki/Universally_unique_identifier#Versions
		https://docs.python.org/2/library/uuid.html
		https://stackoverflow.com/a/28776880/3429748

	:type variant:  int
	:param variant: uuid variant to be used. check given links for details.
	                default variant=4, which means random using the OS provided (pseudo)random number generators.

	:type uuid_base:  uuid object
	:param uuid_base: "base uuid" to generate a new uuid when using either variant 3 or 5, together with a passed string 'uuid_string'.

	:type uuid_string:  string
	:param uuid_string: String to create a new uuid together with uuid_base for either variant 3 or 5.
						Two created uuids with same 'uuid_base' and 'uuid_string' will be identic, so 'uuid_string' should be unique.
	"""

	if variant==1:
		uuid_hash = uuid.uuid1()										# uses MAC adress + Datetime

	elif variant==3:
		try:
			uuid_hash = uuid.uuid3(uuid_base,uuid_string)				# uses MD5 algorithm for hashing
		except AttributeError:
			uuid_hash = uuid.uuid3(uuid.NAMESPACE_URL,uuid_string)		# uses MD5 algorithm for hashing
			print(u"WARNING:    Uuid namespace (base uuid) is no valid uuid object. Used uuid.NAMESPACE_URL ('6ba7b811-9dad-11d1-80b4-00c04fd430c8') instead.")

	elif variant==4:
		uuid_hash = uuid.uuid4()										# uses os random number generator

	elif variant==5:
		try:
			uuid_hash = uuid.uuid5(uuid_base,uuid_string)				# uses SHA1 algorithm for hashing
		except AttributeError:
			uuid_hash = uuid.uuid5(uuid.NAMESPACE_URL,uuid_string)		# uses SHA1 algorithm for hashing
			print(u"WARNING:    Uuid namespace (base uuid) is no valid uuid object. Used uuid.NAMESPACE_URL ('6ba7b811-9dad-11d1-80b4-00c04fd430c8') instead.")

	else:
		print(u'WARNING:    Uuid variant %s not valid (only 1, 3, 4, or 5). Used instead variant 4 (random number).' % variant)
		uuid_hash = uuid.uuid4()

	return str(uuid_hash)


###  infra-structure  ###
def timed_job(interval_in_s, job, *args, **kwargs):

	""" 
	Executes function 'job' all 'interval_in_s' seconds, together with arguement
	'*args' and keyword argument '**kwargs'.

	Code works that way, that after having processed 'job', the rest of the time
	until 'interval_in_s' is reach, the this script sleeps. 

	If execution time takes longer than 'interval_in_s' (i.e., ValueError),
	no further sleeping is applied and next iteration exectuted right away.

	There shouldn't be any shift in start times of job, as it is the case
	with other options. 
	"""

	time_in_s = time.time()
	while True:
		
		print(u"Execute '%s', on: %s (UTC %+dh)" % (job.__name__, dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), int(-time.timezone/3600) ))
		job(*args, **kwargs)
		print(u'')

		time_in_s += interval_in_s;
		try:
			time.sleep(time_in_s - time.time())			# if negative, i.e., job took longer than 'interval_in_s', it raises ValueError
		except ValueError as err:
			pass 										# no sleeping, i.e., go right away into next iteration and do job
def ablauf(hostname_news_page):

	"""


	"""

	articles             = get_articles(hostname_news_page, forget_articles_of_last_time=False)
	better_articles      = [BetterArticle(article) for article in articles]
	better_articles      = [article for article in better_articles if article.is_datetime==True]	# select only such that have a datetime parsed (i.e. =True)

	if better_articles:																				# not empty
		for artikel in better_articles:
			artikel.show()
			#print(artikel)
		print(u'%s news.' % len(better_articles))
	
	else:																							# emtpy
		print(u'No news.')
def get_articles(hostname_news_page, forget_articles_of_last_time=True):

	"""
	Pass hostname of news paper page. E.g.: "http://www.finanznachrichten.de"
	Download, parse and return atricles as list of 'article' object
	"""

	# random user_agent
	user_agent     = random_useragent()

	# get news from page
	news_page      = newspaper.build(hostname_news_page, language='de', memoize_articles=forget_articles_of_last_time, fetch_images=False, browser_user_agent=user_agent)
	articles       = news_page.articles

	return articles


######################  main  ######################
def main():

	"""
	Main program.
	"""

	hostname_news_page   = u'http://www.finanznachrichten.de'
	hostname_news_page   = u'http://www.finanznachrichten.de/nachrichten-aktien/alibaba-group-holding-ltd-adr.htm'
	

	#Thread               = threading.Thread(target=timed_job, args=(600, ablauf, hostname_news_page), kwargs={})
	#Thread.daemon = True
	#Thread.start()
	#print(threading.currentThread())
	#print(threading.enumerate())
	#print(threading.activeCount())

	#def f(name):
	#	print('hello', name)
	#
	#p = multiprocessing.Process(target=f, args=('bob',))
	#p.start()
	#p.join()


######################  _ _ N A M E _ _ = = " _ _ M A I N _ _ "  ##############
if __name__ == "__main__":
	argues = sys.argv
	eval(argues[1])

