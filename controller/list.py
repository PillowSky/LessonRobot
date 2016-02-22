# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

from urllib import urlencode
from urlparse import parse_qs, urlparse
from tornado.gen import coroutine, Return
from tornado.web import authenticated
from tornado.httpclient import HTTPError
from pyquery import PyQuery
from controller.base import BaseHandler

class ListHandler(BaseHandler):
	@authenticated
	@coroutine
	def get(self):
		page = int(self.get_argument('page', 1))

		#request my page to verify login
		try:
			myRes = yield self.client.fetch(self.myUrl, headers=self.cookieHeader, follow_redirects=False)
		except HTTPError as e:
			self.redirect(self.get_login_url())
			raise Return()

		#request firstPage
		courseTable = {}
		def extractList(i, e):
			if i > 0:
				d = PyQuery(e)
				courseID = int(parse_qs(urlparse(d('a').attr('href')).query)['id'][0])
				name = d('a').attr('title')
				status = d('td:last-child').text()
				if status == u'已选':
					status = 2
				elif status == u'点击进入':
					status = 0
				courseTable[courseID] = [name, status]

		def extractMy(i, e):
			d = PyQuery(e)
			courseID = int(parse_qs(urlparse(d('a').attr('href')).query)['id'][0])
			if courseID in courseTable:
				courseTable[courseID][1] = 1

		firstRes = yield self.client.fetch(self.courseListUrl, headers=self.cookieHeader)
		d = PyQuery(firstRes.body.decode('utf-8', 'ignore'))

		#pageCount
		pageText = d('[style="float:left;width:40%;"]').text()
		pageCount = int(pageText[pageText.index(u'共')+1:pageText.index(u'页')])

		#request later page
		if page != 1:
			postData = {
				'__EVENTTARGET': 'ctl10$AspNetPager1',
				'__EVENTARGUMENT': page,
				'__VIEWSTATE': d('#__VIEWSTATE').attr('value'),
				'__EVENTVALIDATION': d('#__EVENTVALIDATION').attr('value'),
			}
			pageRes = yield self.client.fetch(self.courseListUrl, method='POST', headers=self.cookieHeader, body=urlencode(postData))
			d = PyQuery(pageRes.body.decode('utf-8', 'ignore'))

		#extractList
		d('#ctl10_gvCourse tr').each(extractList)

		#process myCourse at last
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
			'page': page,
			'pageCount': pageCount
		}

		courseList = [[name, value[0], value[1]] for name, value in courseTable.iteritems()]
		courseList.reverse()
		self.render('list.html', info=info, courseList=courseList)
