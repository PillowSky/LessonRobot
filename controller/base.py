from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
	referer_url = 'http://www.0575study.gov.cn'
	login_url = 'http://www.0575study.gov.cn/login'
	course_list_url = 'http://www.0575study.gov.cn/course/courseCenterContent'
	my_course_url = 'http://www.0575study.gov.cn/myspace/mycourse'
	my_info_url = 'http://www.0575study.gov.cn/myspace/userinfo'
	course_url = 'http://www.0575study.gov.cn/course/courseContent'
	play_url = 'http://www.0575study.gov.cn/course/coursePlay'
	progress_url = 'http://www.0575study.gov.cn/course/courseWarePlayMemory'

	def initialize(self):
		self.client = AsyncHTTPClient()
		self.session_header = {
			'Cookie': self.request.headers.get('Cookie', ''),
			'User-Agent': self.request.headers.get('User-Agent', ''),
			'Referer': self.referer_url
		}

	def get_current_user(self):
		return self.get_cookie('JSESSIONID')
