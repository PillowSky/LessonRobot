# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

import os
import string
import subprocess
from Cookie import SimpleCookie
from datetime import datetime, timedelta
from pyquery import PyQuery
from random import randrange
from urllib import urlencode
from urlparse import parse_qs, urlparse

from fake_useragent import UserAgent
from tornado.gen import coroutine, sleep, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError

class LessonRobot(object):
	referer_url = 'http://www.qzce.gov.cn'
	login_url = 'http://www.qzce.gov.cn/login.aspx?from=changeuser'
	kick_url = 'http://www.qzce.gov.cn/Login.aspx?Kick=True&UserId='
	course_list_url = 'http://www.qzce.gov.cn/Course/Default.aspx'
	my_url = 'http://www.qzce.gov.cn/my/Default.aspx'
	course_url = 'http://www.qzce.gov.cn/course/Course.aspx?id='
	play_url = 'http://www.qzce.gov.cn/play/play.aspx?course_id='
	progress_url = 'http://www.qzce.gov.cn/play/AICCProgressNew.ashx'
	redirect_url = 'http://www.qzce.gov.cn/play/redirect.aspx'

	def __init__(self):
		super(LessonRobot, self).__init__()
		self.client = AsyncHTTPClient()
		self.session_header = {
			'User-Agent': UserAgent().random,
			'Referer': self.referer_url
		}
		self.cookiejar = SimpleCookie()

	@coroutine
	def login(self, username, password):
		self.username = username

		r = yield self.client.fetch(self.login_url, headers=self.session_header)
		d = PyQuery(r.body.decode('gb2312', 'ignore'))
		body = {
			"__VIEWSTATE": d('#__VIEWSTATE').attr('value'),
			"__EVENTVALIDATION": d('#__EVENTVALIDATION').attr('value'),
			"ctl00$cp$Login1$UserName": username,
			"ctl00$cp$Login1$Password": password,
			"ctl00$cp$Login1$LoginButton.x": 25,
			"ctl00$cp$Login1$LoginButton.y": 10
		}

		try:
			r = yield self.client.fetch(self.login_url, method='POST', headers=self.session_header, body=urlencode(body), follow_redirects=False)
			if 'Set-Cookie' in r.headers:
				try:
					r = yield self.client.fetch(self.kick_url + str(username), headers=self.session_header, follow_redirects=False)
				except HTTPError as e:
					r = e.response
				for c in r.headers.get_list('Set-Cookie'):
					self.cookiejar.load(c)
				self.load_cookie()
				raise Return(True)
			else:
				raise Return(False)
		except HTTPError as e:
			r = e.response
			for c in r.headers.get_list('Set-Cookie'):
				self.cookiejar.load(c)
			self.load_cookie()
			raise Return(True)

	def load_cookie(self):
		self.session_header['Cookie'] = '; '.join(["%s=%s" % (k, v.value) for k, v in self.cookiejar.iteritems()])

	@coroutine
	def page_count(self):
		r = yield self.client.fetch(self.course_list_url, headers=self.session_header)
		for c in r.headers.get_list('Set-Cookie'):
			self.cookiejar.load(c)
		self.load_cookie()

		d = PyQuery(r.body.decode('gb2312', 'ignore'))
		text = d('[style="float:left;width:40%;"]').text()
		count = int(text[text.index(u'共')+1:text.index(u'页')])

		raise Return(count)

	@coroutine
	def page(self, page):
		course_list = []

		def extract_list(i, e):
			if i > 0:
				d = PyQuery(e)
				courseID = int(parse_qs(urlparse(d('a').attr('href')).query)['id'][0])
				course_list.append(courseID)

		first_res = yield self.client.fetch(self.course_list_url, headers=self.session_header)
		d = PyQuery(first_res.body.decode('gb2312', 'ignore'))

		body = {
			'__EVENTTARGET': 'ctl00$ctl00$ctl00$cp$cp$cp$AspNetPager1',
			'__EVENTARGUMENT': page,
			'__VIEWSTATE': d('#__VIEWSTATE').attr('value'),
			'__EVENTVALIDATION': d('#__EVENTVALIDATION').attr('value'),
			'ctl00$ctl00$ctl00$cp$cp$cp$SearchPortfolio1$ckFinish': 'on'
		}

		page_res = yield self.client.fetch(self.course_list_url, method='POST', headers=self.session_header, body=urlencode(body))
		d = PyQuery(page_res.body.decode('gb2312', 'ignore'))

		#extract_list
		d('#ctl00_ctl00_ctl00_cp_cp_cp_gvCourse tr').each(extract_list)

		raise Return(course_list)

	@coroutine
	def learn(self, courseID):
		#register
		r = yield self.client.fetch(self.course_list_url, headers=self.session_header)
		d = PyQuery(r.body.decode('gb2312', 'ignore'))

		query = {
			'id': courseID,
			'user_id': self.username
		}

		try:
			r = yield self.client.fetch(self.redirect_url + '?' + urlencode(query), headers=self.session_header, follow_redirects=False)
		except HTTPError as e:
			pass

		#get username, sid_list and start play
		r, _ = yield [self.client.fetch(self.course_url + str(courseID), headers=self.session_header), self.client.fetch(self.play_url + str(courseID), headers=self.session_header)]
		d = PyQuery(r.body.decode('gb2312', 'ignore'))

		sid_list = d('#ctl00_ctl00_ctl00_cp_cp_cp_Panel1 table td:last-child').text().split(' ')

		#initParam
		body = {
			"method": "initParam",
			"courseID": courseID,
			"userID": self.username
		}
		yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header, body=urlencode(body))

		#learn all
		for sid in sid_list:
			if 'S' in sid:
				#start one
				body = {
					'method': 'setParam',
					'lastLocation': 0,
					'SID': sid,
					'curtime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					'STime': 1,
					'state': 'S',
					'courseID': courseID,
					'userID': self.username
				}
				yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header, body=urlencode(body))
				yield sleep(1)

				#finish one
				body = {
					'method': 'setParam',
					'lastLocation': 10050,
					'SID': sid,
					'curtime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					'STime': 1,
					'state': 'C',
					'courseID': courseID,
					'userID': self.username
				}
				yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header, body=urlencode(body))
