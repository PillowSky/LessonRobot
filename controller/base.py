# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient

class BaseHandler(RequestHandler):
	domainUrl = 'http://www.sygj.org.cn/'
	loginUrl = 'http://www.sygj.org.cn/login.aspx?from=changeuser'
	kickUrl = 'http://www.sygj.org.cn/Login.aspx?Kick=True&UserId='
	courseListUrl = 'http://www.sygj.org.cn/Course/Default.aspx'
	myUrl = 'http://www.sygj.org.cn/my/Default.aspx'
	courseUrl = 'http://www.sygj.org.cn/course/Course.aspx?id='
	playUrl = 'http://www.sygj.org.cn/play/play.aspx?course_id='
	progressUrl = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'
	vcodeUrl = 'http://www.sygj.org.cn/inc/CodeImg.aspx'

	def initialize(self):
		self.client = AsyncHTTPClient()
		self.cookieHeader = {
			'Cookie': self.request.headers.get('Cookie', ''),
			'User-Agent': self.request.headers.get('User-Agent', ''),
			'Referer': self.domainUrl
		}

	def get_current_user(self):
		return self.get_cookie('ASP.NET_SessionId') and self.get_cookie('.ASPXAUTH')
