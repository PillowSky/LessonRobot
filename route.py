from controller.index import IndexHandler
from controller.list import ListHandler

route = [
	(r'/', IndexHandler),
	(r'/list', ListHandler),
]
