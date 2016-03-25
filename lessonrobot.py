# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

import os
import string
import subprocess
from Cookie import SimpleCookie
from datetime import datetime, timedelta
from pyquery import PyQuery
from random import randrange
from urllib import urlencode
from urlparse import parse_qs, urlparse

from fake_useragent import UserAgent
from tornado.gen import coroutine, sleep, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop

class LessonRobot(object):
	referer_url = 'http://www.sygj.org.cn'
	login_url = 'http://www.sygj.org.cn/login.aspx?from=changeuser'
	kick_url = 'http://www.sygj.org.cn/Login.aspx?Kick=True&UserId='
	course_list_url = 'http://www.sygj.org.cn/Course/Default.aspx'
	my_url = 'http://www.sygj.org.cn/my/Default.aspx'
	course_url = 'http://www.sygj.org.cn/course/Course.aspx?id='
	play_url = 'http://www.sygj.org.cn/play/play.aspx?course_id='
	progress_url = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'
	vcode_url = 'http://www.sygj.org.cn/inc/CodeImg.aspx'

	def __init__(self):
		super(LessonRobot, self).__init__()
		self.client = AsyncHTTPClient()
		self.session_header = {
			'User-Agent': UserAgent().random,
			'Referer': self.referer_url
		}
		self.cookiejar = SimpleCookie()

	@coroutine
	def login(self, username, password):
		self.username = username

		r = yield self.client.fetch(self.login_url, headers=self.session_header)
		vcode = yield self.recognize_vcode(username)

		d = PyQuery(r.body.decode('utf-8', 'ignore'))
		body = {
			"__VIEWSTATE": d('#__VIEWSTATE').attr('value'),
			"__EVENTVALIDATION": d('#__EVENTVALIDATION').attr('value'),
			"ctl05$UserName": username,
			"ctl05$Password": password,
			"ctl05$txtCode": vcode,
			"ctl05$LoginButton.x": 36,
			"ctl05$LoginButton.y": 10
		}

		try:
			r = yield self.client.fetch(self.login_url, method='POST', headers=self.session_header, body=urlencode(body), follow_redirects=False)
			if 'Set-Cookie' in r.headers:
				raise Return(True)
			else:
				raise Return(False)
		except HTTPError as e:
			raise Return(True)

	@coroutine
	def recognize_vcode(self, username):
		while True:
			r = yield self.client.fetch(self.vcode_url, headers=self.session_header)
			for c in r.headers.get_list('Set-Cookie'):
				self.cookiejar.load(c)
			self.load_cookie()

			vcode_file = "/tmp/%s.gif" % username
			with open(vcode_file, 'w') as vcode_out:
				vcode_out.write(r.buffer.getvalue())
			crop_cmd = "convert {} -resize 56x20! -crop 14x20 {}_%d{}".format(vcode_file, *os.path.splitext(vcode_file))
			subprocess.check_call(crop_cmd, shell=True)
			os.remove(vcode_file)

			token = []
			for i in range(4):
				part_name = "{}_%d{}".format(*os.path.splitext(vcode_file)) % i
				color_cmd = "convert {} -scale 1x1\! -format '%[pixel:u]' info:-".format(part_name)
				color_rgb = subprocess.check_output(color_cmd, shell=True)
				fill_name = "{}_%d_fill{}".format(*os.path.splitext(vcode_file)) % i
				fill_cmd = "convert {} -fill white -fuzz 40% -opaque '{}' {}".format(part_name, color_rgb, fill_name)
				subprocess.check_call(fill_cmd, shell=True)
				tesseract_cmd = "tesseract %s stdout -psm 10 -l eng nobatch digits" % fill_name
				tesseract_answer = subprocess.check_output(tesseract_cmd, stderr=DEVNULL, shell=True)
				token.append(string.strip(tesseract_answer))

				os.remove(part_name)
				os.remove(fill_name)

			answer = ''.join(token)
			if len(answer) == 4:
				raise Return(answer)

	def load_cookie(self):
		self.session_header['Cookie'] = '; '.join(["%s=%s" % (k, v.value) for k, v in self.cookiejar.iteritems()])
