import os
from tornado.ioloop import IOLoop
from index import application

port = int(os.getenv('PORT', 8000))
application.listen(port)
print("Tornado server listen on port {}".format(port))
IOLoop.instance().start()
