from urllib import urlencode
from Cookie import SimpleCookie
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPError
from pyquery import PyQuery

class OnlineHandler(RequestHandler):
	loginUrl = 'http://www.sygj.org.cn/login.aspx?from=changeuser'
	kickUrl = 'http://www.sygj.org.cn/Login.aspx?Kick=True&UserId='
	courseListUrl = 'http://www.sygj.org.cn/Course/Default.aspx'
	myUrl = 'http://www.sygj.org.cn/my/Default.aspx'
	courseUrl = 'http://www.sygj.org.cn/course/Course.aspx?id='
	playUrl = 'http://www.sygj.org.cn/play/play.aspx?course_id='
	progressUrl = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'

	def initialize(self):
		self.client = AsyncHTTPClient()

	@coroutine
	def login(self, username, password):
		r = yield self.client.fetch(self.loginUrl)
		d = PyQuery(r.body.decode('utf-8', 'ignore'))

		#login
		postData = {
			"__VIEWSTATE": d('#__VIEWSTATE').attr('value'),
			"__EVENTVALIDATION": d('#__EVENTVALIDATION').attr('value'),
			"hidPageID": d('#hidPageID').attr('value'),
			"ctl05$hdIsDefault": d('#ctl05_hdIsDefault').attr('value'),
			"ctl05$UserName": username,
			"ctl05$Password": password,
			"ctl05$LoginButton.x": 36,
			"ctl05$LoginButton.y": 10
		}
		try:
			r = yield self.client.fetch(self.loginUrl, method='POST', body=urlencode(postData), follow_redirects=False)
		except HTTPError as e:
			if e.code == 302:
				r = e.response
			else:
				raise NotImplementedError('TODO')

		#kick
		if 'confirm' in r.body:
			try:
				r = yield self.client.fetch(self.kickUrl + str(username), follow_redirects=False)
			except HTTPError as e:
				if e.code == 302:
					r = e.response
				else:
					raise NotImplementedError('TODO')

		cookieJar = SimpleCookie(r.headers['Set-Cookie'].replace('path=/,', 'path=/;').replace('HttpOnly,', 'HttpOnly;'))
		self.cookieString = '; '.join(['%s=%s' % (item.key, item.value) for item in cookieJar.itervalues()])
