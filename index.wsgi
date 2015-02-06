from tornado.web import Application
from route import route
from secret import cookie_secret

application = Application(
	handlers = route,
	template_path = 'view',
	static_path = 'static',
	login_url = '/login',
	cookie_secret = cookie_secret,
	debug = True,
)
