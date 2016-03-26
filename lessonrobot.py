import re
from Cookie import SimpleCookie
from datetime import datetime, timedelta
from pyquery import PyQuery
from random import randrange
from urllib import urlencode
from urlparse import parse_qs, urlparse

from fake_useragent import UserAgent
from tornado.gen import coroutine, sleep, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop

from pymongo import MongoClient

mongoUrl = "mongodb://localhost/region"
region = MongoClient(mongoUrl)['region']['region']

class LessonRobot(object):
	referer_url = 'http://www.zjce.gov.cn'
	login_url = 'http://www.zjce.gov.cn/login'
	course_list_url = 'http://www.zjce.gov.cn/course/courseCenterContent'
	my_course_url = 'http://www.zjce.gov.cn/myspace/mycourse'
	my_info_url = 'http://www.zjce.gov.cn/myspace/userinfo'
	course_url = 'http://www.zjce.gov.cn/course/courseContent'
	play_url = 'http://www.zjce.gov.cn/course/coursePlay'
	progress_url = 'http://www.zjce.gov.cn/course/courseWarePlayMemory'

	def __init__(self):
		super(LessonRobot, self).__init__()
		self.client = AsyncHTTPClient()
		self.session_header = {
			'User-Agent': UserAgent().random,
			'Referer': self.referer_url
		}

	@coroutine
	def login(self, username, password):
		body = {
			'username': username,
			'password': password,
			'from': 'index',
			'rememberMe': 'off'
		}
		try:
			r = yield self.client.fetch(self.login_url, method='POST', headers=self.session_header,
										body=urlencode(body), follow_redirects=False)
		except HTTPError as e:
			r = e.response
			url = r.headers['Location']
			if not 'error' in url:
				domain = urlparse(url).netloc
				document = {
					'username': username,
					'domain': domain,
					'url': url
				}
				print(username, domain)
				region.update({'username': username}, document, True)
			else:
				print('[Failed]', username)