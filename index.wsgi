from tornado.web import Application
from route import route

application = Application(
	handlers = route,
	template_path = "view",
	static_path = "static",
	debug = True,
)
