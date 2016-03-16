from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from urllib import urlencode

from controller.base import BaseHandler


class LoginHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.render('login.html', error=False)

	@coroutine
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')

		success = yield self.login(username, password)
		if success:
			self.render('success.html')
		else:
			self.render('login.html', error=True)

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
				for c in r.headers.get_list('Set-Cookie'):
					self.add_header('Set-Cookie', c)
				raise Return(True)
			else:
				raise Return(False)
