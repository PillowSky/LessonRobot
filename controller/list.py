# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from urllib import urlencode
from urlparse import parse_qs, urlparse
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

		#request first coursepage and mypage
		courseTable = {}
		def extractList(i, e):
			if i > 0:
				d = PyQuery(e)
				id = parse_qs(urlparse(d('a').attr('href')).query)['id'][0]
				name = d('a').attr('title')
				status = d('td:last-child').text()
				courseTable[id] = [name, status]

		def extractMy(i, e):
			d = PyQuery(e)
			id = parse_qs(urlparse(d('a').attr('href')).query)['id'][0]
			courseTable[id][1] = u'正在学习'

		firstReq = HTTPRequest(self.courseListUrl, headers={'Cookie': self.cookieString})
		myReq = HTTPRequest(self.myUrl, headers={'Cookie': self.cookieString})

		firstRes, myRes = yield [self.client.fetch(firstReq), self.client.fetch(myReq)]

		d = PyQuery(firstRes.body.decode('utf-8', 'ignore'))
		d('#ctl10_gvCourse tr').each(extractList)

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
			batchRequest.append(HTTPRequest(self.courseListUrl, method='POST', headers={'Cookie': self.cookieString}, body=urlencode(postData)))

		batchResponse = yield [self.client.fetch(req) for req in batchRequest]

		for r in batchResponse:
			d = PyQuery(r.body.decode('utf-8', 'ignore'))
			d('#ctl10_gvCourse tr').each(extractList)
		
		#process myPage at last
		d = PyQuery(myRes.body.decode('utf-8', 'ignore'))
		d('#MyCourseList li.list4 a').each(extractMy)
		name = d('#UCUserLogin b').text()
		score = d('#UCUserLogin li:nth-child(6)').text().split(' ')[-1]

		print(name)
		print(score)
		print(len(courseTable))