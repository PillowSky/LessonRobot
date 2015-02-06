from controller.index import IndexHandler
from controller.login import LoginHandler
from controller.list import ListHandler
from controller.learn import LearnHandler

route = [
	(r'/', IndexHandler),
	(r'/login', LoginHandler),
	(r'/list', ListHandler),
	(r'/learn', LearnHandler),
]
