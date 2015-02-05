# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

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

		#request first page
		courseList = {}
		def extract(i, e):
			d = PyQuery(e)
			key = d('a').attr('title')
			value = d('td:last-child').text()
			if key and value:
				courseList[d('a').attr('title')] = d('td:last-child').text()

		r = yield self.client.fetch(self.courseListUrl, headers={'Cookie': self.cookieString})

		d = PyQuery(r.body.decode('utf-8', 'ignore'))
		d('#ctl10_gvCourse tr').each(extract)

		#request later page
		pageText = d('[style="float:left;width:40%;"]').text()
		count = int(pageText[pageText.index(u'共') + 1]) + 1

		batchRequest = []
		for i in range(2, count):
			postData = {
				'__EVENTTARGET': 'ctl10$AspNetPager1',
				'__EVENTARGUMENT': i,
				'__VIEWSTATE': d('#__VIEWSTATE').attr('value'),
				'__EVENTVALIDATION': d('#__EVENTVALIDATION').attr('value'),
				'hidPageID': 294,
				'ctl05$hdIsDefault': 1,
				'selectSearch': 'txtKeyword',
				'ctl10$HFID': ''
			}
			pageRequest.append(HTTPRequest(self.courseListUrl, method='POST', headers={'Cookie': self.cookieString}, body=urlencode(postData)))

		batchResponse = yield [self.client.fetch(req) for req in pageRequest]

		for r in batchResponse:
			d = PyQuery(r.body.decode('utf-8', 'ignore'))
			d('#ctl10_gvCourse tr').each(extract)
