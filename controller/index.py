from tornado.web import authenticated

from controller.base import BaseHandler


class IndexHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('success.html')