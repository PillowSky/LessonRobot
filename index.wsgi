import os
from tornado.web import Application
from controller.index import IndexHandler
from controller.login import LoginHandler
from controller.list import ListHandler
from controller.learn import LearnHandler
from controller.vcode import VcodeHandler

route = [
	(r'/', IndexHandler),
	(r'/login', LoginHandler),
	(r'/list', ListHandler),
	(r'/learn', LearnHandler),
	(r'/vcode', VcodeHandler)
]

application = Application(
	handlers = route,
	template_path = os.path.join(os.path.dirname(__file__), 'view'),
	static_path = os.path.join(os.path.dirname(__file__), 'static'),
	login_url = '/login'
)
