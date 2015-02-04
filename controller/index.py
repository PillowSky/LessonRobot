from tornado import version
from tornado.web import RequestHandler

class IndexHandler(RequestHandler):
	def get(self):
		print(dir(self))
		self.render('index.html')
