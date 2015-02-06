# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from tornado.web import authenticated
from controller.base import BaseHandler

class IndexHandler(BaseHandler):
	@authenticated
	def get(self):
		self.render('success.html')
