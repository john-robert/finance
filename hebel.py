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
import smtplib
import datetime as dt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

#from secrets.util import gmail_auth								# private libaries
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate



import newspaper
import fake_useragent
import pandas_datareader.data as web
import pandas as pd
import requests
import csv
from apscheduler.schedulers.background import BackgroundScheduler


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
		self.log      = open(self.logfile, "a")

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
def get_google_finance_intraday(ticker, period=60, days=1):
    """
    Retrieve intraday stock data from Google Finance.

    Parameters
    ----------
    ticker : str
        Company ticker symbol.
    period : int
        Interval between stock values in seconds.
    days : int
        Number of days of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the opening price, high price, low price,
        closing price, and volume. The index contains the times associated with
        the retrieved price values.
    """

    uri = 'https://finance.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,o,h,l,c,v&df=cpct&q={ticker}'.format(ticker=ticker,
                                                                          period=period,
                                                                          days=days)
    page = requests.get(uri)
    print(uri)
    reader = csv.reader(page.content.splitlines())
    columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))

###  e-mail  ###
def validMail(mail):

	"""
	Check if passed variable 'mail' is string. If not, make it string.
	Then, check if 'mail' matches e-mail pattern, if yes, return mail with
	preceding and succeeding white blancs stripped.
	If pattern isn't matched, return False (without doing lstrip() / rstrip())
	
	:return: mail / False 
	"""

	if not isinstance(mail, str) or not re.search(r"\w.@\w+\.\w+", mail):
		sys.exit(u'ERROR:    Given SENDER adress is no valid e-mail string. Exit.')
	return mail.lstrip().rstrip()
def valid_listMail(list_adresses):

	"""
	Check if passed list is a list, if yes, check if entries are valid mail
	adresses. Strips preceding and succeeding white blancs. Return a list only 
	with valid adresses, if there is no valid adress at all, return empty list.
	
	:return list_adress
	"""
	
	adresses = []
	if isinstance(list_adresses, list):
		pass
	elif isinstance(list_adresses, tuple):
		list_adresses = list(list_adresses)
	elif isinstance(list_adresses, str):
		list_adresses = [list_adresses]
	else:
		sys.exit(u'ERROR:    Given ADDRESSES are no valid list or tuple format. Exit.')
		
	for adress in list_adresses:
		if validMail(adress):
			adresses.append(adress)

	return adresses
def headerMail(msgBasis, sender, recipients, carbon, bcarbon, replyto, subject):

	"""
	Fill header information of passed 'msgBasis' instance. 
	
	:return: 'msgBasis' and all other passed variable
	"""

	# date
	msgBasis['Date'] = formatdate(localtime=True)		# dt.datetime.now().strftime('%Y-%m-%d, %H:%M Uhr')
	#print(msgBasis['Date'])
	
	# sender
	msgBasis['From'] = validMail(sender)

	# recipients
	recipients       = valid_listMail(recipients)
	msgBasis['To']   = ', '.join(recipients)
	
	# carbon copies
	carbon           = valid_listMail(carbon)
	msgBasis['Cc']   = ', '.join(carbon)
	
	# blind carbon copies
	bcarbon          = valid_listMail(bcarbon)
	msgBasis['Bcc']  = ', '.join(bcarbon)
	
	# reply-to
	replyto          = valid_listMail(replyto)		
	msgBasis.add_header('reply-to', ', '.join(replyto))
	
	# subject
	try:
		msgBasis['Subject'] = str(subject)
	except:
		msgBasis['Subject'] = ''

	# preamble
	msgBasis.preamble = "PREAMBLE:   How to learn sending e-mails with Python's SMTP!"
	
	return msgBasis, recipients, carbon, bcarbon, replyto
def attachmentsMail(msgBasis, attachments):

	"""
	Attach files past as list 'attachments' to e-mail message 'msgBasis' instance.
	If given attachment cannot be found, it is removed from list.
	
	:return: 'msgBasis' (e-mail message instance) & 'attachments'
	"""

	### check if attachments is list (or can be converted to
	try:
		attachments = [str(ele) for ele in attachments]
	except:
		sys.exit(u'ERROR:    Given ATTACHMENTS are no valid list or tuple format of strings. Exit.')

	### attach files, if can not be found, state warning and delete from attachment list
	for i in range(len(attachments)):

		part = MIMEBase('application', "octet-stream")
		try: 
			part.set_payload(open(file, "rb").read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
			msgBasis.attach(part)
		except: 
			print(u"WARNING:    Attachment '%s' not found and thus not attached." % file)
			continue
		
	return msgBasis
def connectSMPT(client, username, password):

	"""
	Connect to SMTP mail server.
	
	:return: smtplib server
	"""

	try:
		if client.lower() == 'tls':
			try:
				server = smtplib.SMTP('smtp.gmail.com', 587)
				server.ehlo()
				#server.esmtp_features['starttls']
				server.starttls()
				server.ehlo()
				server.login(username,password)
				return server
			except Exception as err:
				print(u"WARNING:     Couldn't establish '%s' connection to server. Proceed with 'ssh', port '465'. Error message:\n%s" % (client, err))  
				server.quit()
				client = 'ssl'

		if client.lower() == 'ssl':
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(username,password)
			return server
		
		if client.lower() == 'localhost':
			command = 'python3 -m smtpd -n localhost:25'
			server  = smtplib.SMTP('localhost', 25)
			server.set_debuglevel(1)
			return server

		sys.exit(u"ERROR:    You want to connect to a SMTP server which is not known of the time being (choose 'localhost' or 'gmail'). Exit.")

	except smtplib.SMTPHeloError as err:
		sys.exit(u"ERROR:    Sever didn't reply properly to HELO GREETING! Exit.")

	except smtplib.SMTPAuthenticationError as err:
		sys.exit(u"ERROR:    Username and/or password not accepted to connect to SMTP server! Exit.")

	except smtplib.socket.error as err:
		if client.lower() == 'localhost':
			print(u'Did you started a local SMTP server? If not, try:%s' % command)
		sys.exit(u"ERROR:    Couldn't connect to '%s' server. Error message:\n%s." % (client, err))

	except smtplib.SMTPServerDisconnected as err: 
		sys.exit(u'ERROR:    Just try again! Error message:\n%s.' % err)

	except Exception as err:
		sys.exit(u'ERROR:    Error message:\n%s' % err)
def sendMail(sender, recipients, cc=[], bcc=[], replyto=[], subject='', text='', attachments=[], connection='ssl'):
			
	"""
	
	"""

	### Mail container
	msgBasis                               = MIMEMultipart('mixed')
	
	### Mail header
	msgBasis, recipients, cc, bcc, replyto = headerMail(msgBasis, sender, recipients, cc, bcc, replyto, subject)
	
	### Mail attachments
	msgBasis                               = attachmentsMail(msgBasis, attachments)

	### Mail send via SMPT
	username, password                     = gmail_auth()
	server                                 = connectSMPT(connection, username, password)
	#server.verify(sender)
	server.sendmail(sender, recipients + cc + bcc, text)
	server.quit()

######################  main  ######################
def main():

	"""
	Main program.
	"""

	sched = BackgroundScheduler()

	def job_function():
		print("Hello World")
		time.sleep(5)


	print(dt.datetime.now())

	# Schedules job_function to be run on the third Friday
	# of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
	sched.add_job(job_function, 'cron', second=1)
	sched.start()

######################  _ _ N A M E _ _ = = " _ _ M A I N _ _ "  ##############
if __name__ == "__main__":
	argues = sys.argv
	eval(argues[1])