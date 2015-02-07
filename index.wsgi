import os
from tornado.web import Application
from route import route
from secret import cookie_secret

application = Application(
	handlers = route,
	template_path = os.path.join(os.path.dirname(__file__), 'view'),
	static_path = os.path.join(os.path.dirname(__file__), 'static'),
	login_url = '/login',
	cookie_secret = cookie_secret,
)
