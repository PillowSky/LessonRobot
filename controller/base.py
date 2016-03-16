from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    domainUrl = 'http://www.0575study.gov.cn'
    loginUrl = 'http://www.0575study.gov.cn/login'
    courseListUrl = 'http://www.0575study.gov.cn/course/courseCenterContent'
    myCourseUrl = 'http://www.0575study.gov.cn/myspace/mycourse?page='
    myInfoUrl = 'http://www.0575study.gov.cn/myspace/userinfo'
    courseUrl = 'http://www.sygj.org.cn/course/Course.aspx?id='
    playUrl = 'http://www.sygj.org.cn/play/play.aspx?course_id='
    progressUrl = 'http://www.sygj.org.cn/play/AICCProgressNew.ashx'

    def initialize(self):
        self.client = AsyncHTTPClient()
        self.cookieHeader = {
            'Cookie': self.request.headers.get('Cookie', ''),
            'User-Agent': self.request.headers.get('User-Agent', ''),
            'Referer': self.domainUrl
        }

    def get_current_user(self):
        return self.get_cookie('JSESSIONID')