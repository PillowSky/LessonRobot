from pyquery import PyQuery
from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from tornado.web import authenticated
from urllib import urlencode
from urlparse import parse_qs, urlparse

from controller.base import BaseHandler


class ListHandler(BaseHandler):
	@authenticated
	@coroutine
	def get(self):
		page = int(self.get_argument('page', 0))
		page_count = 0
		course_list = []

		# fetch my_info and verify login
		try:
			my_info_res = yield self.client.fetch(self.my_info_url, headers=self.session_header, follow_redirects=False)
		except HTTPError as e:
			self.redirect(self.get_login_url())
			raise Return()

		# fetch learning course
		if page == 0:
			def extract_my(i, e):
				d = PyQuery(e)
				course_id = parse_qs(urlparse(d('.my_study_tr a[target]').attr('href')).query)['cwAcademyId'][0]
				name = d('.my_study_tr a[target]').text()
				course_list.append([course_id, name, 1])

			first_res = yield self.client.fetch(self.my_course_url, headers=self.session_header)
			d = PyQuery(first_res.body.decode('utf-8'))
			d('body > li[style]').each(extract_my)

			my_course_count = len(d('a[style]'))
			if my_course_count > 1:
				batch_res = yield [self.client.fetch(self.my_course_url + '?' + urlencode({'page': i}), headers=self.session_header) for i in range(2, my_course_count + 1)]
				for r in batch_res:
					d = PyQuery(r.body.decode('utf-8'))
					d('body > li[style]').each(extract_my)

			if len(course_list) == 0:
				page = 1
			else:
				page_res = yield self.fetch_page(1)
				d = PyQuery(page_res.body.decode('utf-8'))
				page_count = int(d('.con_pagelist a').eq(-2).text())

		# fetch unlearned course
		if page != 0:
			def extract_list(i, e):
				d = PyQuery(e)
				course_id = parse_qs(urlparse(d('td > a').attr('href')).query)['cwAcademyId'][0]
				name = d('td > a').text()
				course_list.append([course_id, name, 0])

			page_res = yield self.fetch_page(page)
			d = PyQuery(page_res.body.decode('utf-8'))
			d('.con_item_list li').each(extract_list)
			page_count = int(d('.con_pagelist a').eq(-2).text())

		d = PyQuery(my_info_res.body.decode('utf-8'))
		info = {
			'name': d('.mybox').text().split(' ')[0],
			'score': d('.con_mybox li').eq(3).find('span').text(),
			'graduate': d('.con_mybox li').eq(2).find('span').text(),
			'page': page,
			'page_count': page_count
		}

		self.render('list.html', info=info, course_list=course_list)

	def fetch_page(self, page):
		query = {
			'currentPage': page,
			'onlyShowNoMylr': 1
		}
		return self.client.fetch(self.course_list_url + '?' + urlencode(query), headers=self.session_header)
