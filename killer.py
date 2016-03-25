import signal
import logging
import time
import json
from tornado.gen import coroutine, sleep
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from lessonrobot import LessonRobot

concurrency = 8
q = Queue(maxsize=1000)

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO)
AsyncHTTPClient.configure(None, max_clients=1000)

accounts_ok = []
accounts_fail = []

@coroutine
def worker():
	while True:
		username = yield q.get()
		logging.info('[Get] %s' % username)

		try:
			robot = LessonRobot()
			for i in range(10):
				logging.info('[Try] %s: %d/10' % (username, i+1))
				result = yield robot.login(username, username)
				if result:
					logging.info('[Login] %s' % username)
					accounts_ok.append(username)
					break
				else:
					if i == 9:
						logging.info('[Failed] %s' % username)
						accounts_fail.append(username)
		except Exception as e:
			logging.info('[Exception] %s:%s' % (username, e))
			yield q.put(username)
		q.task_done()

@coroutine
def spawner():
	accounts = []
	with open('accounts.json') as accounts_file:
		accounts = json.loads(accounts_file.read())
	for username in accounts:
		yield q.put(username)
		logging.info('[Put] %s' % username)
		yield sleep(1)

@coroutine
def main():
	for i in xrange(concurrency):
		IOLoop.current().spawn_callback(worker)

	yield spawner()
	yield q.join()

	with open('accounts_ok.json', 'w') as fout:
		fout.write(json.dumps(accounts_ok))

	with open('accounts_fail.json', 'w') as fout:
		fout.write(json.dumps(accounts_fail))

	logging.info('All Done')

IOLoop.current().run_sync(main)
