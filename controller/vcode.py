# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from tornado.gen import coroutine
from controller.base import BaseHandler

class VcodeHandler(BaseHandler):
	@coroutine
	def get(self):
		r = yield self.client.fetch(self.vcodeUrl, headers=self.cookieHeader)
		self.set_status(r.code)

		for name, value in r.headers.iteritems():
			self.set_header(name, value)

		self.write(r.buffer.getvalue())
