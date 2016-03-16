import os
from tornado.ioloop import IOLoop
from tornado.web import Application

from controller.index import IndexHandler
from controller.learn import LearnHandler
from controller.list import ListHandler
from controller.login import LoginHandler

route = [
	(r'/', IndexHandler),
	(r'/login', LoginHandler),
	(r'/list', ListHandler),
	(r'/learn', LearnHandler)
]

application = Application(
	handlers=route,
	template_path=os.path.join(os.path.dirname(__file__), 'view'),
	static_path=os.path.join(os.path.dirname(__file__), 'static'),
	login_url='/login'
)

if __name__ == '__main__':
	port = int(os.getenv('PORT', 8000))
	application.listen(port)
	print("Tornado server listen on port {}".format(port))
	IOLoop.instance().start()
