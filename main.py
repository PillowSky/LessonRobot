from tornado.ioloop import IOLoop
from index import application

port = 8888
application.listen(port)
print("Tornado server listen on port {}".format(port))
IOLoop.instance().start()
