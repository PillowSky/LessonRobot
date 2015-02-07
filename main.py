from tornado.ioloop import IOLoop
from index import application

application.listen(8000)
IOLoop.instance().start()
