from tornado.ioloop import IOLoop
from index import application

port = 8000
application.listen(port)
print("Tornado Server Listen on port {}".format(port))
IOLoop.instance().start()
