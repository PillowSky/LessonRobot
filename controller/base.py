from urllib import urlencode
from Cookie import SimpleCookie
from tornado.gen import coroutine, Return
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPError
from pyquery import PyQuery

class BaseHandler(RequestHandler):
	loginUrl = 'http://www.sygj.org.cn/login.aspx?from=changeuser'
	kickUrl = 'http://www.sygj.org.cn/Login.aspx?Kick=True&UserId='
	courseListUrl = 'http://www.sygj.org.cn/Course/Default.aspx'
	myUrl = 'http://www.sygj.org.cn/my/Default.aspx'
	courseUrl = 'http://www.sygj.org.cn/course/Course.aspx?id='
	playUrl = 'http://www.sygj.org.cn/play/play.aspx?course_id='
	progressUrl = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'

	def initialize(self):
		self.client = AsyncHTTPClient()

	def get_current_user(self):
		return self.get_secure_cookie("username")

	@coroutine
	def validate(self, username, password):
		r = yield self.tryLogin(username, password)

		if 'Set-Cookie' in r.headers:
			raise Return(True)
		else:
			raise Return(False)

	@coroutine
	def login(self, username, password):
		r = yield self.tryLogin(username, password)

		if 'confirm' in r.body:
			r = yield self.kick(username)

		cookieJar = SimpleCookie(r.headers['Set-Cookie'].replace('path=/,', 'path=/;').replace('HttpOnly,', 'HttpOnly;'))
		self.cookieString = '; '.join(['%s=%s' % (item.key, item.value) for item in cookieJar.itervalues()])

	@coroutine
	def tryLogin(self, username, password):
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

		raise Return(r)

	@coroutine
	def kick(self, username):
		try:
			r = yield self.client.fetch(self.kickUrl + str(username), follow_redirects=False)
		except HTTPError as e:
			if e.code == 302:
				r = e.response
			else:
				raise NotImplementedError('TODO')

		raise Return(r)
