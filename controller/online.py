import requests
from urllib import urlencode
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from pyquery import PyQuery

class OnlineHandler(RequestHandler):
	loginUrl = 'http://www.sygj.org.cn/login.aspx?from=changeuser'
	kickUrl = 'http://www.sygj.org.cn/Login.aspx?Kick=True&UserId='
	courseListUrl = 'http://www.sygj.org.cn/Course/Default.aspx'
	courseUrl = 'http://www.sygj.org.cn/course/Course.aspx?id='
	playUrl = 'http://www.sygj.org.cn/play/play.aspx?course_id='
	progressUrl = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'

	def initialize(self):
		self.client = AsyncHTTPClient()
		self.session = requests.Session()

	@coroutine
	def login(self, username, password):
		r = yield self.client.fetch(self.loginUrl)
		d = PyQuery(r.body.decode(errors='ignore'))

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
		r = self.session.post(self.loginUrl, data=postData, allow_redirects=False)

		#kick
		if 'confirm' in r.text:
			self.session.get(self.kickUrl + str(username), allow_redirects=False)
		
		self.cookieString = urlencode(self.session.cookies).replace('&', '; ')
