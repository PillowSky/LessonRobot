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
	(r'/vcode', VcodeHandler),
]
