from datetime import datetime, timedelta
from pyquery import PyQuery
from tornado.gen import coroutine, Task
from tornado.httpclient import HTTPError
from tornado.ioloop import IOLoop
from tornado.web import authenticated
from urllib import urlencode

from controller.base import BaseHandler


class LearnHandler(BaseHandler):
	@authenticated
	@coroutine
	def post(self):
		courseID = self.get_argument('courseID')

		# register
		r = yield self.client.fetch(self.course_list_url, headers=self.session_header)
		d = PyQuery(r.body.decode('utf-8', 'ignore'))

		postData = {
			'__EVENTTARGET': '',
			'__EVENTARGUMENT': '',
			'__VIEWSTATE': d('#__VIEWSTATE').attr('value'),
			'__EVENTVALIDATION': d('#__EVENTVALIDATION').attr('value'),
			'ctl10$gvCourse$ctl20$checkone': courseID,
			'ctl10$HFID': ',%s,' % courseID,
			'ctl10$btnMuti.x': '51',
			'ctl10$btnMuti.y': '11'
		}

		try:
			r = yield self.client.fetch(self.course_list_url, method='POST', headers=self.session_header,
										body=urlencode(postData))
		except HTTPError as e:
			pass

		# get username, sidList and start play
		r, _ = yield [self.client.fetch(self.course_url + str(courseID), headers=self.session_header),
					  self.client.fetch(self.play_url + str(courseID), headers=self.session_header)]
		d = PyQuery(r.body.decode('utf-8', 'ignore'))

		onclick = d('.Course_Main_box_body_02 input[type=button]').attr('onclick')
		username = onclick[onclick.index('user_id=') + 8:onclick.index("','")]

		sidList = d('.table2 table td:last-child').text().split(' ')
		del sidList[0]

		# initParam
		postData = {
			"method": "initParam",
			"courseID": courseID,
			"userID": username
		}
		yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header, body=urlencode(postData))

		unitDelta = timedelta(seconds=1)
		# learn all
		for sid in sidList:
			# start one
			postData = {
				'method': 'setParam',
				'lastLocation': 0,
				'SID': sid,
				'curtime': datetime.now().isoformat(' '),
				'STime': 1,
				'state': 'S',
				'courseID': courseID,
				'userID': username
			}
			r = yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header,
										body=urlencode(postData))

			yield Task(IOLoop.instance().add_timeout, unitDelta)

			# finish one
			postData = {
				'method': 'setParam',
				'lastLocation': 10050,
				'SID': sid,
				'curtime': (datetime.now() + unitDelta).isoformat(' '),
				'STime': 1,
				'state': 'C',
				'courseID': courseID,
				'userID': username
			}
			r = yield self.client.fetch(self.progress_url, method='POST', headers=self.session_header,
										body=urlencode(postData))

		if 'null' in r.body:
			self.write('ok')
		else:
			self.write('more')
