# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from urllib import urlencode
from urlparse import parse_qs, urlparse
from tornado.gen import coroutine
from tornado.web import authenticated
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from pyquery import PyQuery
from controller.base import BaseHandler

class ListHandler(BaseHandler):
	@authenticated
	@coroutine
	def get(self):
		username = self.get_secure_cookie('username')
		password = self.get_secure_cookie('password')

		yield self.login(username, password)

		#request first coursepage and mypage
		courseTable = {}
		def extractList(i, e):
			if i > 0:
				d = PyQuery(e)
				id = int(parse_qs(urlparse(d('a').attr('href')).query)['id'][0])
				name = d('a').attr('title')
				status = d('td:last-child').text()
				if status == u'已选':
					status = 2
				elif status == u'点击进入':
					status = 0
				courseTable[id] = [name, status]

		def extractMy(i, e):
			d = PyQuery(e)
			id = int(parse_qs(urlparse(d('a').attr('href')).query)['id'][0])
			courseTable[id][1] = 1

		firstRes, myRes = yield [self.client.fetch(self.courseListUrl, headers={'Cookie': self.cookieString}), self.client.fetch(self.myUrl, headers={'Cookie': self.cookieString})]

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

		done, now, no = [0, 0, 0]
		for status in courseTable.itervalues():
			if status[1] == 0:
				no += 1
			elif status[1] == 2:
				done += 1
			elif status[1] == 1:
				now += 1

		info = {
			'name': d('#UCUserLogin b').text(),
			'score': d('#UCUserLogin li:nth-child(6)').text().split(' ')[-1],
			'rank': d('#UCUserLogin li:nth-child(8)').text().split(' ')[-1],
			'total': len(courseTable),
			'done': done,
			'now': now,
			'no': no,
		}

		courseList = [[id, value[0], value[1]] for id, value in courseTable.iteritems()]
		courseList.sort(None, None, True)
		self.render('list.html', info=info, courseList=courseList)
