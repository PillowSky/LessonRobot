from controller.index import IndexHandler
from controller.login import LoginHandler
from controller.list import ListHandler

route = [
	(r'/', IndexHandler),
	(r'/login', LoginHandler),
	(r'/list', ListHandler),
]
