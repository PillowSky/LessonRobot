from tornado.gen import coroutine
from controller.base import BaseHandler

class LoginHandler(BaseHandler):
	def get(self):
		self.render('login.html', error=False)

	@coroutine
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')

		success = yield self.validate(username, password)
		if success:
			self.set_secure_cookie("username", username)
			self.set_secure_cookie("password", password)
			self.render('success.html')
		else:
			self.render('login.html', error=True)