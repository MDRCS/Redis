import redis
import time

conn = redis.Redis()

def no_trans():
    print(conn.incr('notrans:'))
    time.sleep(.1)
    conn.incr('notrans:', -1)


"""
>>> if 1:
...     for i in xrange(3):
...         threading.Thread(target=notrans).start()
...     time.sleep(.5)

1
2
3

- Because there’s no transaction, each of the threaded commands can interleave freely, causing the counter to steadily grow in this case.
"""

def trans():
    pipeline = conn.pipeline()
    pipeline.incr('trans:')
    time.sleep(.1)
    pipeline.incr('trans:', -1)
    print(pipeline.execute()[0])

"""
>>> if 1:
        for i in xrange(3):
            threading.Thread(target=trans).start()
        time.sleep(.5)
1
1
1

Because each increment/sleep/decrement pair is executed inside a transaction, no other commands can be interleaved, which gets us a result of 1 for all of our results.
"""
