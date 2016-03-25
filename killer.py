import signal
import logging
import time
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from lessonrobot import LessonRobot

concurrency = 10
q = Queue(maxsize=1000)

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO)
AsyncHTTPClient.configure(None, max_clients=1000)

spawn_timestamp = time.time()
exception_timestamp = time.time()

@coroutine
def worker():
	global concurrency, spawn_timestamp, exception_timestamp
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
					now_timestamp = time.time()
					if now_timestamp - exception_timestamp > 60 and now_timestamp - spawn_timestamp > 60:
						concurrency += 1
						IOLoop.current().spawn_callback(worker)
						spawn_timestamp = now_timestamp
						logging.info('[Spawn] concurrency = %d' % concurrency)
				logging.info('[Done] %s' % username)
			else:
				logging.info('[Failed] %s' % username)
		except Exception as e:
			logging.info('[Exception] %s:%s' % (username, e))
			yield q.put(username)

			last_timestamp = exception_timestamp
			exception_timestamp = time.time()
			if exception_timestamp - last_timestamp < 10:
				if concurrency > 1:
					q.task_done()
					concurrency -= 1
					logging.info('[Reduce] concurrency = %d' % concurrency)
					break
				else:
					yield sleep(60)

		q.task_done()

@coroutine
def spawner():
	for i in xrange(257000, 258000):
		username = 'zjce%06d' % i
		yield q.put(username)
		logging.info('[Put] %s' % username)
		yield sleep(1)

def handler_USR1(signum, frame):
	global concurrency
	concurrency += 1
	logging.info('[Signal] %d: concurrency = %d' % (signum, concurrency))
	IOLoop.current().spawn_callback(worker)

signal.signal(signal.SIGUSR1, handler_USR1)

@coroutine
def main():
	for i in xrange(concurrency):
		IOLoop.current().spawn_callback(worker)

	yield spawner()
	yield q.join()
	logging.info('All Done')

IOLoop.current().run_sync(main)
