from tornado import version
from tornado.web import RequestHandler

class ListHandler(RequestHandler):
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')
		self.write(username + password)