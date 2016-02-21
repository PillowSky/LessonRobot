# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from urllib import urlencode
from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from pyquery import PyQuery
from controller.base import BaseHandler

class LoginHandler(BaseHandler):
	def get(self):
		if self.get_cookie('.ASPXAUTH'):
			self.clear_cookie('.ASPXAUTH')
		if self.get_cookie('guidcookie1'):
			self.clear_cookie('guidcookie1')
		self.render('login.html', error=False)

	@coroutine
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')
		vcode = self.get_argument('vcode')

		success = yield self.login(username, password, vcode)
		if success:
			self.render('success.html')
		else:
			self.render('login.html', error=True)

	@coroutine
	def login(self, username, password, vcode):
		r = yield self.client.fetch(self.loginUrl, headers=self.cookieHeader)
		d = PyQuery(r.body.decode('utf-8', 'ignore'))

		postData = {
			"__VIEWSTATE": d('#__VIEWSTATE').attr('value'),
			"__EVENTVALIDATION": d('#__EVENTVALIDATION').attr('value'),
			"ctl05$UserName": username,
			"ctl05$Password": password,
			"ctl05$txtCode": vcode,
			"ctl05$LoginButton.x": 36,
			"ctl05$LoginButton.y": 10
		}

		try:
			r = yield self.client.fetch(self.loginUrl, method='POST', headers=self.cookieHeader, body=urlencode(postData), follow_redirects=False)
			if 'Set-Cookie' in r.headers:
				try:
					r = yield self.client.fetch(self.kickUrl + str(username), headers=self.cookieHeader, follow_redirects=False)
				except HTTPError as e:
					r = e.response
				for c in r.headers.get_list('Set-Cookie'):
					self.add_header('Set-Cookie', c)
				raise Return(True)
			else:
				raise Return(False)
		except HTTPError as e:
			r = e.response
			for c in r.headers.get_list('Set-Cookie'):
				self.add_header('Set-Cookie', c)
			raise Return(True)
