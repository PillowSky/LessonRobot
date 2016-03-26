# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

import string
from pyquery import PyQuery
from urllib import urlencode

from fake_useragent import UserAgent
from tornado.gen import coroutine, sleep, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError

class LessonRobot(object):
	referer_url = 'http://www.hzgb.gov.cn'
	login_url = 'http://www.hzgb.gov.cn/login.aspx?from=changeuser'
	kick_url = 'http://www.hzgb.gov.cn/Login.aspx?Kick=True&UserId='
	course_list_url = 'http://www.hzgb.gov.cn/Course/Default.aspx'
	my_url = 'http://www.hzgb.gov.cn/my/Default.aspx'
	course_url = 'http://www.hzgb.gov.cn/course/Course.aspx?id='
	play_url = 'http://www.hzgb.gov.cn/play/play.aspx?course_id='
	progress_url = 'http://www.hzgb.gov.cn/play/AICCProgressNew.ashx'
	redirect_url = 'http://www.hzgb.gov.cn/play/redirect.aspx'

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
			"__VIEWSTATEGENERATOR": d('__VIEWSTATEGENERATOR').attr('value'),
			"__EVENTVALIDATION": d('#__EVENTVALIDATION').attr('value'),
			"ctl00$cp$Login1$UserName": username,
			"ctl00$cp$Login1$Password": password,
			"ctl00$cp$Login1$LoginButton": (u'+登++录+').encode('utf-8')
		}

		try:
			r = yield self.client.fetch(self.login_url, method='POST', headers=self.session_header, body=urlencode(body), follow_redirects=False)
			raise Return(False)
		except HTTPError as e:
			if e.code == 302:
				raise Return(True)
			else:
				raise e
