from datetime import datetime, timedelta
from pyquery import PyQuery
from random import randrange
from tornado.gen import coroutine, Task, Return
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.web import authenticated
from urllib import urlencode
from urlparse import parse_qs, urlparse

from controller.base import BaseHandler


class LearnHandler(BaseHandler):
	@authenticated
	@coroutine
	def post(self):
		academyId = self.get_argument('academyId')

		# fetch course page and register
		course_res, play_res = yield [self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}), headers=self.session_header), self.client.fetch(self.play_url + '?' + urlencode({'cwAcademyId': academyId}), headers=self.session_header)]

		d = PyQuery(play_res.body.decode('utf-8'))
		qs = parse_qs(urlparse(d('#playframe').attr('src')).query)
		courseID = qs['courseID'][0]
		userID = qs['userID'][0]

		if 'index.html' in d('#playframe').attr('src'):
			d = PyQuery(course_res.body.decode('utf-8'))
			section_status = d('.learning_style01, .learning_style02').map(lambda i, e: ('S%03d' % (i+1), PyQuery(e).hasClass('learning_style01')))

			#initParam
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
				yield Task(IOLoop.instance().add_timeout, timedelta(seconds=1))

				query = {
					'method': 'setParam',
					'lastLocation': randrange(10**7, 10**8),
					'SID': sid,
					'curtime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					'STime': 1,
					'state': 'C',
					'courseID': courseID,
					'userID': userID
				}
				yield self.client.fetch(self.progress_url + '?' + urlencode(query), headers=self.session_header)
				raise Return()

			#first learn
			if len(section_status) == 0:
				yield learn_section('S001')

				course_res = yield self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}), headers=self.session_header)
				d = PyQuery(course_res.body.decode('utf-8'))
				section_status = d('.learning_style01, .learning_style02').map(lambda i, e: ('S%03d' % (i+1), PyQuery(e).hasClass('learning_style01')))

			for sid, status in section_status:
				if not status:
					yield learn_section(sid)
		else:
			d = PyQuery(course_res.body.decode('utf-8'))
			section_status = d('.learning_style01, .learning_style02').map(lambda i, e: (i+1, PyQuery(e).hasClass('learning_style01')))

			#scomInitParam
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

			#first learn
			if len(section_status) == 0:
				yield learn_section(1)

				course_res = yield self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}), headers=self.session_header)
				d = PyQuery(course_res.body.decode('utf-8'))
				section_status = d('.learning_style01, .learning_style02').map(lambda i, e: (i+1, PyQuery(e).hasClass('learning_style01')))
		
			for sid, status in section_status:
				if not status:
					yield learn_section(sid)

		#verify
		course_res = yield self.client.fetch(self.course_url + '?' + urlencode({'cwAcademyId': academyId}), headers=self.session_header)
		d = PyQuery(course_res.body.decode('utf-8'))

		if len(d('.learning_style01')) > 0 and len(d('.learning_style02')) == 0:
			self.write('ok')
		else:
			self.write('more')
