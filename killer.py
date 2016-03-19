from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.httpclient import HTTPError
from lessonrobot import LessonRobot

concurrency = 10
q = Queue(maxsize=concurrency)


@coroutine
def consumer():
    while True:
        username = yield q.get()
        robot = LessonRobot()
        result = yield robot.login(username, '123456')

        if result:
            print('[Login] %s' % username)
            try:
                count = yield robot.page_count()
                for i in xrange(count + 1):
                    course_list = yield robot.page(i)
                    print('[Page] %s: %d/%d => %d' % (username, i, count, len(course_list)))
                    for course in course_list:
                        print('[Learn] %s: %s' % (username, course))
                        result = yield robot.learn(course)
                        if result:
                            print('[Ok] %s: %s' % (username, course))
                        else:
                            print('[More] %s: %s' % (username, course))
                print('[Done] %s' % username)
            except HTTPError as e:
                print('[HTTPError] %s' % username)
                yield q.put(username)
        else:
            print('[Invalid] %s' % username)

        q.task_done()


@coroutine
def producer():
    for i in xrange(200000, 200004):
        username = 'sxce%06d' % i
        yield q.put(username)
        print('[Start] %s' % username)


@coroutine
def main():
    for i in xrange(concurrency):
        IOLoop.current().spawn_callback(consumer)

    yield producer()
    yield q.join()
    print('All Done')

IOLoop.current().run_sync(main)