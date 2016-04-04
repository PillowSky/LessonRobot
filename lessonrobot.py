# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from pyquery import PyQuery
from urllib import urlencode
from urlparse import urlparse

from fake_useragent import UserAgent
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError

from pymongo import MongoClient

mongoUrl = "mongodb://localhost/hunan"

class LessonRobot(object):
	referer_url = 'http://www.hngbjy.com'
	login_url = 'http://www.hngbjy.com/login.aspx'

	def __init__(self):
		super(LessonRobot, self).__init__()
		self.client = AsyncHTTPClient()
		self.session_header = {
			'User-Agent': UserAgent().random,
			'Referer': self.referer_url
		}

	@coroutine
	def login(self, username, password):
		r = yield self.client.fetch(self.login_url, headers=self.session_header)
		d = PyQuery(r.body.decode('utf-8', 'ignore'))
		body = {
			"__VIEWSTATE": d('#__VIEWSTATE').attr('value'),
			"__VIEWSTATEGENERATOR": d('#__VIEWSTATEGENERATOR').attr('value'),
			"ctl05$UserName": username,
			"ctl05$Password": password,
			"ctl05$LoginButton.x": 36,
			"ctl05$LoginButton.y": 10
		}

		try:
			r = yield self.client.fetch(self.login_url, method='POST', headers=self.session_header, body=urlencode(body), follow_redirects=False)
			raise Return(False)
		except HTTPError as e:
			r = e.response
			url = r.headers['Location']
			document = {
				'username': username,
				'domain': urlparse(url).netloc,
				'url': url
			}
			region = MongoClient(mongoUrl)['hunan']['region']
			region.update({'username': username}, document, True)
			raise Return(True)
