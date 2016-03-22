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


class LessonRobot(object):
	referer_url = 'http://www.0575study.gov.cn'
	login_url = 'http://www.0575study.gov.cn/login'
	course_list_url = 'http://www.0575study.gov.cn/course/courseCenterContent'
	my_course_url = 'http://www.0575study.gov.cn/myspace/mycourse'
	my_info_url = 'http://www.0575study.gov.cn/myspace/userinfo'
	course_url = 'http://www.0575study.gov.cn/course/courseContent'
	play_url = 'http://www.0575study.gov.cn/course/coursePlay'
	progress_url = 'http://www.0575study.gov.cn/course/courseWarePlayMemory'

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
			if 'JSESSIONID' in r.headers['Set-Cookie']:
				self.session_header['Cookie'] = 'JSESSIONID=' + SimpleCookie(r.headers['Set-Cookie'])['JSESSIONID'].value
				raise Return(True)
			else:
				raise Return(False)

	@coroutine
	def page_count(self):
		r = yield self.fetch_page(1)
		d = PyQuery(r.body.decode('utf-8'))
		count = int(d('.con_pagelist a').eq(-2).text())

		raise Return(count)

	@coroutine
	def page(self, page):
		course_list = []

		if page == 0:
			def extract_my(i, e):
				d = PyQuery(e)
				course_id = parse_qs(urlparse(d('.my_study_tr a[target]').attr('href')).query)['cwAcademyId'][0]
				course_list.append(course_id)

			first_res = yield self.client.fetch(self.my_course_url, headers=self.session_header)
			d = PyQuery(first_res.body.decode('utf-8'))
			d('body > li[style]').each(extract_my)

			my_course_count = len(d('a[style]'))
			if my_course_count > 1:
				batch_res = yield [
					self.client.fetch(self.my_course_url + '?' + urlencode({'page': i}), headers=self.session_header)
					for i in range(2, my_course_count + 1)]
				for r in batch_res:
					d = PyQuery(r.body.decode('utf-8'))
					d('body > li[style]').each(extract_my)

		# fetch unlearned course
		if page != 0:
			def extract_list(i, e):
				d = PyQuery(e)
				course_id = parse_qs(urlparse(d('td > a').attr('href')).query)['cwAcademyId'][0]
				course_list.append(course_id)

			page_res = yield self.fetch_page(page)
			d = PyQuery(page_res.body.decode('utf-8'))
			d('.con_item_list li').each(extract_list)

		raise Return(course_list)

	def fetch_page(self, page):
		query = {
			'currentPage': page,
			'onlyShowNoMylr': 1
		}

		return self.client.fetch(self.course_list_url + '?' + urlencode(query), headers=self.session_header)

	@coroutine
	def learn(self, academyId):
		# fetch course page and register
		course_res, play_res = yield [self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}),
														headers=self.session_header),
									  self.client.fetch(self.play_url + '?' + urlencode({'cwAcademyId': academyId}),
														headers=self.session_header)]

		d = PyQuery(play_res.body.decode('utf-8'))
		qs = parse_qs(urlparse(d('#playframe').attr('src')).query)
		courseID = qs['courseID'][0]
		userID = qs['userID'][0]

		if 'index.html' in d('#playframe').attr('src'):
			d = PyQuery(course_res.body.decode('utf-8'))
			section_status = d('.learning_style01, .learning_style02').map(
				lambda i, e: ('S%03d' % (i + 1), PyQuery(e).hasClass('learning_style01')))

			# initParam
			query = {
				'method': 'initParam',
				'courseID': courseID,
				'userID': userID,
			}
			yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)

			@coroutine
			def learn_section(sid):
				query = {
					'method': 'setParam',
					'lastLocation': 0,
					'SID': sid,
					'curtime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					'STime': 1,
					'state': 'S',
					'courseID': courseID,
					'userID': userID
				}
				yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)
				yield sleep(1)

				query = {
					'method': 'setParam',
					'lastLocation': randrange(10 ** 7, 10 ** 8),
					'SID': sid,
					'curtime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					'STime': 1,
					'state': 'C',
					'courseID': courseID,
					'userID': userID
				}
				yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)

			# first learn
			if len(section_status) == 0:
				yield learn_section('S001')

				course_res = yield self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}),
													 headers=self.session_header)
				d = PyQuery(course_res.body.decode('utf-8'))
				section_status = d('.learning_style01, .learning_style02').map(
					lambda i, e: ('S%03d' % (i + 1), PyQuery(e).hasClass('learning_style01')))

			for sid, status in section_status:
				if not status:
					yield learn_section(sid)
		else:
			d = PyQuery(course_res.body.decode('utf-8'))
			section_status = d('.learning_style01, .learning_style02').map(
				lambda i, e: (i + 1, PyQuery(e).hasClass('learning_style01')))

			# scomInitParam
			query = {
				'method': 'scomInitParam',
				'courseID': courseID,
				'userID': userID,
			}
			yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)

			@coroutine
			def learn_section(sid):
				query = {
					'method': 'scomSetParam',
					'courseID': courseID,
					'userID': userID,
					'SID': 60 * sid,
					'STime': randrange(6000, 10000),
					'interval': 60
				}
				yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)

			# first learn
			if len(section_status) == 0:
				yield learn_section(1)

				course_res = yield self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}),
													 headers=self.session_header)
				d = PyQuery(course_res.body.decode('utf-8'))
				section_status = d('.learning_style01, .learning_style02').map(
					lambda i, e: (i + 1, PyQuery(e).hasClass('learning_style01')))

			for sid, status in section_status:
				if not status:
					yield learn_section(sid)
