import signal
import logging
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from lessonrobot import LessonRobot

concurrency = 250
q = Queue(maxsize=10)

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.NOTSET)
AsyncHTTPClient.configure(None, max_clients=1000)

@coroutine
def consumer():
	while True:
		username = yield q.get()
		logging.info('[Get] %s' % username)

		try:
			robot = LessonRobot()
			result = yield robot.login(username, '123456')
			if result:
				logging.info('[Login] %s' % username)
				count = yield robot.page_count()
				for i in xrange(count + 1):
					course_list = yield robot.page(i)
					course_len = len(course_list)
					logging.info('[Page] %s: %d/%d => %d' % (username, i, count, course_len))
					if course_len == 0 and i != 0:
						raise Exception('Session Expired')
					for course in course_list:
						logging.info('[Learn] %s: %s' % (username, course))
						yield robot.learn(course)
				logging.info('[Done] %s' % username)
			else:
				logging.info('[Failed] %s' % username)
		except Exception as e:
			logging.info('[Exception] %s:%s' % (username, e))
			yield q.put(username)

		q.task_done()

@coroutine
def producer():
	for i in xrange(200000, 201000):
		username = 'sxce%06d' % i
		yield q.put(username)
		logging.info('[Put] %s' % username)
		yield sleep(1)

def handler(signum, frame):
	step = 10
	logging.info('[Signal] %d: concurrency += %d' % (signum, step))
	for i in xrange(step):
		IOLoop.current().spawn_callback(consumer)

signal.signal(signal.SIGUSR1, handler)

@coroutine
def main():
	for i in xrange(concurrency):
		IOLoop.current().spawn_callback(consumer)

	yield producer()
	yield q.join()
	logging.info('All Done')

IOLoop.current().run_sync(main)
