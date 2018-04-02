#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
""" Box of self-written helper functions for Python3. """
#   Date:      Feb 2018
#   License:   GPLv3
#---------------------------------------------------------------------


###############  INITIATION  ##############
__title__ = u'kampfname'
__author__ = u'John-Robert Scholz'


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

# libaries that need extra installation (e.g. via conda, pip, or directly from source code)
import newspaper
import numpy as np
import fake_useragent
import dateutil as du
import matplotlib.pyplot as plt
import alpha_vantage.timeseries as ts
import pandas as pd
pd.set_option('display.width', 100)


######################  CLASSES & FUNCTIONS  ######################
###  important  ###
class BetterArticle:

	"""

	"""


	def __init__(self, article, **kwargs):

		article.build()

		match                  = re.search(r'(\d{2}.\d{2}.\d{4})\s*.\s*(\d{2}:\d{2})', article.html)
		if match:
			date_str           = match.group(1)
			time_str           = match.group(2)
			date_time          = dt.datetime.strptime('%s %s' % (date_str, time_str), '%d.%m.%Y %H:%M') 
			self.has_datetime  = True
		else:
			date_time          = dt.datetime.now()
			self.has_datetime  = False

		self.html              = article.html
		self.url               = article.url
		self.publish_date      = article.publish_date
		self.title             = article.title
		self.authors           = article.authors									# not specified by finanznachrichten.de
		self.text              = article.text										# needs parse
		self.summary           = article.summary									# needs nlp
		self.keywords          = article.keywords									# needs nlp
 
		self.date_time         = date_time
		self.uuid_hash         = make_uuid_hash(variant=5, uuid_base=uuid.NAMESPACE_URL, uuid_string=self.url)
		self.auto_weight       = self._auto_weight()
		self.manu_weight       = 0
		self.is_pickled        = False
		self.pickle_file       = None


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
								u'{}'.format(u'- - - ' * 30, self.url, self.date_time, self.uuid_hash, self.title, ', '.join(self.authors), self.publish_date, self.summary.replace('\n','\n             '), ', '.join(self.keywords), u'- - - ' * 30, )
								 #print(u'TEXT:        %s'  % self.text)
								 #print(u'COMPANIES:   %s'  % ', '.join(self.related_companies))
								 #print(u'REL_TICKER:  %s'  % ', '.join(self.related_stocks))

		return string_representation


	def _auto_weight(self):
		# Google Tensorflow 
		return 0


	def _manu_weight(self):
		print(self)
		weight = input('How do you think this news impacts the related stock(s):  [-3, -2, -1, 0, 1, 2, 3]:\t')
		return weight


	def pickle(self, target_dir):
		# create target_dir if not existing
		if not os.path.isdir( target_dir ):
			os.makedirs( target_dir )

		# pickle article object
		self.is_pickled  = True
		self.pickle_file = os.path.join(target_dir, self.uuid_hash+'.p')
		pickle.dump(self, open(self.pickle_file, 'wb'))
		print(u'Article object pickled: %s' % self.pickle_file)

		# update news_list of company
		news_list = os.path.join(target_dir, 'news_list.txt')
		with open(news_list, 'a') as fp:
			line = '{:>8.2f}{:>8.2f}{:>20s}{:>40s}'.format(self.auto_weight, self.manu_weight, self.date_time.strftime('%Y-%m-%dT%H:%M'), self.uuid_hash+'.p')
			fp.write( '\n' + line)


	#def reassign_related_stocks(self):
	#	self.related_companies, self.related_stocks = self._related_stocks()


	def redo_auto_weight(self):
		self.auto_weight      = self._auto_weight()


	def set_manu_weight(self, weight):
		self.manu_weight      = self._manu_weight()


	def show(self):
		print(self)


	def print(self):
		print(self)
class Equity:

	"""


	"""


	def __init__(self, ticker=u'MSFT', start=None, end=None, alpha_vantage_APIkey=u'7NSGBW8REI0PSVAC', *args, **kwargs):

		self.ticker              = ticker
		self.retrieve_day        = dt.datetime.today()
		self.start, self.end     = self._handle_dates(start, end)
		self.data, self.metadata = self._get_data(alpha_vantage_APIkey)
		self.is_plotsaved        = False
		self.plot_file           = None


	def __str__(self):
		return u'%s (from: %s to: %s)' % (self.ticker, self.data.index[0].strftime("%Y-%m-%d"), self.data.index[-1].strftime("%Y-%m-%d"))


	def _handle_dates(self, start, end):
		# handel start and end date of request
		if start:
			start      = du.parser.parse(start)
		else:
			start      = self.retrieve_day-dt.timedelta(days=1000)
		if end:
			end        = du.parser.parse(end)
		else:
			end        = self.retrieve_day

		if start > end:
			start, end = end, start

		return start, end


	def _get_data(self, alpha_vantage_APIkey):
		# determine output size. Might be time critical, maybe not.
		if self.start >= self.retrieve_day-dt.timedelta(days=140) and self.end >= self.retrieve_day-dt.timedelta(days=140):
			outputsize = 'compact'
		else:
			outputsize = 'full'

		# get data according to specified times
		timeseries     = ts.TimeSeries(key=alpha_vantage_APIkey, output_format='pandas')
		data, metadata = timeseries.get_daily(symbol=self.ticker, outputsize=outputsize)
		data.Date      = pd.to_datetime(data.index, format='%Y-%m-%d')
		data.set_index(data.Date, inplace=True)
		data           = data[self.start:self.end]

		return data, metadata


	def _depickle_objects(self, dir_objects, regex=r'\.p\Z'):
		pickled_objects = [os.path.join(dir_objects,file) for file in os.listdir(dir_objects) if re.search(regex, file)]
		objects         = [pickle.load( open( pickled_object, 'rb' )) for pickled_object in pickled_objects]
		return objects


	def first(self, n=1):
		return self.data.iloc[:n,:]


	def last(self, n=1):
		return self.data.iloc[-n:,:]


	#def update(self):
	#	self.data                = self.data


	def plot(self, columns='3. low', kind='line', start=None, end=None, show=True, return_axis=False, save_dir=None, news_dir=None, **kwargs):

		"""
		columns: default: columns='3. low'. Or choose: columns=['1. open, '2. high', '3. low', '4. close', '5. volume'] or: columns=list(self.data.columns.values)[:-1] or: ...
		kind: 'line', 'bar', 'barh', 'scatter', ... Check: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.html
		"""

		# handle start and end dates only for plotting (actual equity data may have been retrieved for larger times ...)
		if start:
			start           = du.parser.parse(start)
		else:
			start           = self.start
		if end:
			end             = du.parser.parse(end)
		else:
			end             = self.end
		if start > end:
			start, end      = end, start
		plot_data           = self.data[start:end]
		plot_data_first_day = plot_data.index[0].strftime("%Y-%m-%d")
		plot_data_last_day  = plot_data.index[-1].strftime("%Y-%m-%d")

		# plot commands ...
		fig = plt.figure(num=None, figsize=(14, 10), dpi=80, facecolor='w', edgecolor='k')
		ax  = fig.add_subplot(111)
		plot_data.plot(y=columns, kind=kind, ax=ax, lw=2)
		ax.grid(ls='-.', lw=0.5)
		ax.set_ylabel(u'Equity value', fontsize=12)
		ax.set_xlabel(u'Dates (%s trading days)' % len(plot_data), fontsize=12)
		ax.set_title('%s (from: %s to: %s)' % (self.ticker, plot_data_first_day, plot_data_last_day), fontsize=14)
		ax.tick_params(axis='both', which='major', labelsize=10)
		ax.tick_params(axis='both', which='minor', labelsize=9)

		if news_dir:
			ylim       = ax.get_ylim()
			try:
				articles   = self._depickle_objects(news_dir)
				for article in articles:
					if articles.index(article) == 0:	# to avoid more than one label that goes 'News'
						label=u'News'
					else:
						label = None
					ax.plot( [article.date_time,article.date_time], ylim, color='k', lw=0.5, label=label)
					#ax.text()
			except FileNotFoundError as err:
				print(u'Equity plot no news plotted. Error: %s' % err)
		ax.legend(loc='upper left', fontsize=10)
		fig.tight_layout()

		if save_dir:
			# create target_dir if not existing
			if not os.path.isdir( save_dir ):
				os.makedirs( save_dir )

			# save plot
			self.is_plotsaved = True
			self.plot_file    = os.path.join(save_dir, self.ticker+'_'+plot_data_last_day+'.png')
			plt.savefig(self.plot_file)
			print(u'Equity plot stored: %s' % self.plot_file)

		if show:
			plt.show()

		if return_axis:
			return ax
def random_useragent(update_database=False, ua_fallback=u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:54.0) Gecko/20100101 Firefox/54.0'): 

		"""
		Uses fake_useragent libary from:
	
		  https://pypi.python.org/pypi/fake-useragent
	
		- grabs up to date useragent from useragentstring.com
		- randomize with real world statistic via w3schools.com
	
			==> Allows to construct strings of "USER_AGENT". These are used
			in html request headers to send basic information 
			(parse engine, browser, OS, ) to web servers.
		"""


		ua_db_file  = './SUP/fake_useragent%s.json' % fake_useragent.VERSION
		ua          = fake_useragent.UserAgent(path=ua_db_file, fallback=ua_fallback)	# when path given, database file is stored and accessed here
		if update_database:
			ua.update()
		return ua.random 														# random user agent from real world statistic via w3schools.com
def make_uuid_hash(variant=4, uuid_base=uuid.NAMESPACE_URL, uuid_string=None):

	"""
	Create universal unique identifier and return it as string (has 36 characters).

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
def log(self, log_message, logfile=u'./LOG/log.txt'):
	# create target_dir if not existing
	if not os.path.isdir( os.path.dirname(logfile) ):
		os.makedirs( os.path.dirname(logfile) )

	# make log
	with open(logfile, "a") as fp:
		fp.write(log_message)


###  helpers  ###
def get_company_pages(file_company_pages=u'./SUP/deutsche_unternehmen_urls.txt'):
	companies_and_infos = np.loadtxt(file_company_pages)
	return companies_and_infos


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
def ablauf():

	"""


	"""

	company_infos_list   = [[u'http://www.finanznachrichten.de/nachrichten-aktien/alphabet-inc-cl-a.htm', 'GOOG'],
							[u'http://www.finanznachrichten.de/nachrichten-aktien/microsoft-corporation.htm', 'MSFT']]

	for company_news_page, company_ticker in company_infos_list:

		news_dir             = os.path.join('./NEWS',company_ticker)
		articles             = get_articles(company_news_page, forget_articles_of_last_time=True)
		better_articles      = [BetterArticle(article) for article in articles]
		better_articles      = [article for article in better_articles if article.has_datetime==True]	# select only such that have a datetime parsed (i.e. ==True)
	
		if better_articles:																				# not empty
			for artikel in better_articles:
				print(artikel)
				artikel.pickle( news_dir )
			print(u'%s news.' % len(better_articles))

		goo = Equity(company_ticker)
		goo.plot(news_dir=news_dir, save_dir='./PLOTS', show=False)

	
	else:																								# emtpy
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


######################  MAIN FUNCTION  ######################
def main():

	"""
	Main program.
	"""

	timed_job(600, ablauf)

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
	#switch path to directory of this file. It's important for relative paths coded.
	this_file_dir = os.path.dirname(__file__)
	os.chdir( this_file_dir)

	# any passed function+arguments of script will be executed due to those lines
	argues = sys.argv
	eval(argues[1])

