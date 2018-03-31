#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------
#   Filename:  email_custom.py
""" Box of self-written helper functions for Python. """
#   Author:    JRS
#   Date:      Feb 2018
#   License:   GPLv3
#---------------------------------------------------------------------


#---------------------------------------------------------------------
#------------------------ use of: PYTHON 3 ---------------------------
#---------------------------------------------------------------------


# Python standard libaries
import os
import re
import numpy
import pprint
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders

# private libary
import secrets_personal


class Email:

	"""
	Costumized email class based on python's 'email' libary.
	Initiated instances of this class will allow to send e-mails from John's 
	gmail account. The accound username and password are stored in a separate file
	that is not synchronised ...

	TO DO:
		- write method that can detach already attached mail attachments.
	"""

	def __init__(self, sender, recipients, cc=[], bcc=[], replyto=[], subject='', text='', attachments=[], connection='ssl'):

		"""
		Prepares mail container and puts in header, text and attachments, however,
		it does not send mail yet (see 'send()' method).
		"""

		self.sender          = sender
		self.recipients      = recipients
		self.cc              = cc
		self.bcc             = bcc
		self.replyto         = replyto
		self.subject         = subject
		self.text            = text
		self.attachments     = attachments
		self.connection      = connection
		self.is_sent         = False

		# mail container
		self.__msgBasis      = MIMEMultipart('mixed')
		
		# mail header
		self._prepare_headerMail()
		
		# mail attachments
		self._attachmentsMail( self.attachments )


	def send(self):

		username, password                 = secrets_personal.gmail_auth()
		server                             = self._connectSMPT(self.connection, username, password)
		#server.verify(sender)
		server.sendmail(self.sender, self.recipients + self.cc + self.bcc, self.__msgBasis.as_string())
		server.quit()
		self.is_sent                       = True


	def attach(self, file):
		
		self._attachmentsMail( file, single_add=True )


	def detach(self, file):
		# to bon programmed ..
		pass


	def show(self):

		pprint.pprint(self.__dict__)


	def _validMail(self, mail):

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


	def _valid_listMail(self, list_adresses):

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
				if self._validMail(adress):
					adresses.append(adress)

			return adresses


	def _prepare_headerMail(self):

		"""
		Fill header informatione. 
		
		"""

		# preamble
		self.__msgBasis.preamble  = "PREAMBLE:   How to learn sending e-mails with Python's SMTP!"

		# date
		self.__msgBasis['Date']   = formatdate(localtime=True)		# dt.datetime.now().strftime('%Y-%m-%d, %H:%M Uhr')
		#print(msgBasis['Date'])
		
		# sender
		self.__msgBasis['From']   = self._validMail(self.sender)

		# recipients
		self.recipients           = self._valid_listMail(self.recipients)
		self.__msgBasis['To']     = ', '.join(self.recipients)
		
		# carbon copies
		self.cc                   = self._valid_listMail(self.cc)
		self.__msgBasis['Cc']     = ', '.join(self.cc)
		
		# blind carbon copies
		self.bcc                  = self._valid_listMail(self.bcc)
		self.__msgBasis['Bcc']    = ', '.join(self.bcc)
		
		# reply-to
		self.replyto              = self._valid_listMail(self.replyto)		
		self.__msgBasis.add_header('reply-to', ', '.join(self.replyto))

		# subject
		try:
			self.__msgBasis['Subject'] = str(self.subject)
		except:
			self.__msgBasis['Subject'] = ''


	def _attachmentsMail(self, attachments, single_add=False):

		"""
		Attach files past as list 'attachments' to e-mail message 'msgBasis' instance.
		If given attachment cannot be found, it is not attached.
		"""


		if isinstance(attachments, (numpy.ndarray, numpy.generic)):
			pass
		elif isinstance(attachments, list):
			attachments = numpy.array( attachments )
		elif isinstance(attachments, tuple):
			attachments = numpy.array( list(attachments) )
		elif isinstance(attachments, str):
			attachments = numpy.array( [attachments] )
		else:
			sys.exit(u'ERROR:    Given ATTACHMENTS are no valid list or tuple format of strings. Exit.')


		### attach files, if can not be found, state warning and delete from attachment list
		del_ind = []
		for i in range(len(attachments)):

			if attachments[i] in self.attachments:
				continue

			part = MIMEBase('application', "octet-stream")
			try: 
				part.set_payload(open(attachments[i], "rb").read())
				encoders.encode_base64(part)
				part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachments[i]))
				self.__msgBasis.attach(part)
			except Exception:
				del_ind.append(i)
				print(u"WARNING:    Attachment '%s' not found and thus not attached." % attachments[i])
				continue

		# delete faulty attachments from list
		clean_attachments     = list( numpy.delete(attachments,del_ind) )
		if single_add == True:
			self.attachments += clean_attachments
		elif single_add == False:
			self.attachments  = clean_attachments


	def _connectSMPT(self, client, username, password):

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


######################  _ _ N A M E _ _ = = " _ _ M A I N _ _ "  ##############
if __name__ == "__main__":
	argues = sys.argv
	eval(argues[1])
