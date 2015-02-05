import requests
from urllib import urlencode
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from pyquery import PyQuery
from controller.online import OnlineHandler

class ListHandler(OnlineHandler):
	@coroutine
	def get(self):
		username = self.get_argument('username')
		password = self.get_argument('password')

		yield self.login(username, password)
		print(self.cookieString)
		#request first page
