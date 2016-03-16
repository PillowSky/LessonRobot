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
        courseList = []

        # fetch myInfo and verify login
        try:
            myInfoRes = yield self.client.fetch(self.myInfoUrl, headers=self.cookieHeader, follow_redirects=False)
        except HTTPError as e:
            self.redirect(self.get_login_url())
            raise Return()

        d = PyQuery(myInfoRes.body.decode('utf-8'))
        info = {
            'name': d('.mybox').text().split(' ')[0],
            'score': d('.con_mybox li').eq(3).find('span').text(),
            'graduate': d('.con_mybox li').eq(2).find('span').text(),
            'page': page,
            'pageCount': 1
        }

        if page == 0:
            def extractMy(i, e):
                d = PyQuery(e)
                courseID = parse_qs(urlparse(d('.my_study_tr a[target]').attr('href')).query)['cwAcademyId'][0]
                name = d('.my_study_tr a[target]').text()
                courseList.append([courseID, name, 1])

            firstRes = yield self.client.fetch(self.myCourseUrl + '1', headers=self.cookieHeader)
            d = PyQuery(firstRes.body.decode('utf-8'))
            d('body > li[style]').each(extractMy)

            myCourseCount = len(d('a[style]'))
            if myCourseCount > 1:
                batchRes = yield [self.client.fetch(self.myCourseUrl + str(i), headers=self.cookieHeader) for i in
                                  range(2, myCourseCount + 1)]
                for r in batchRes:
                    d = PyQuery(r.body.decode('utf-8'))
                    d('body > li[style]').each(extractMy)
            else:
                if len(courseList) == 0:
                    info['page'] = page = 1

        # page may be set to 0
        if page != 0:
            def extractList(i, e):
                d = PyQuery(e)
                courseID = parse_qs(urlparse(d('td > a').attr('href')).query)['cwAcademyId'][0]
                name = d('td > a').text()
                courseList.append([courseID, name, 0])

            params = {
                'currentPage': page,
                'onlyShowNoMylr': 1
            }
            pageRes = yield self.client.fetch(self.courseListUrl + '?' + urlencode(params), headers=self.cookieHeader)

            d = PyQuery(pageRes.body.decode('utf-8'))
            d('.con_item_list li').each(extractList)

            info['pageCount'] = int(d('.con_pagelist a').eq(-2).text())

        self.render('list.html', info=info, courseList=courseList)