import threading
import time
import redis

conn = redis.Redis()

def publisher(n):
    time.sleep(1)
    for i in range(n):
        conn.publish('channel', i)
        time.sleep(1)

def run_pubsub():
    threading.Thread(target=publisher, args=(3,)).start()
    pubsub = conn.pubsub()
    pubsub.subscribe(['channel'])
    count = 0
    for item in pubsub.listen():
        print(item)
        count += 1
        if count == 4:
            pubsub.unsubscribe()
        if count == 5:
            break

'''
# <start id="pubsub-calls-1"/>
>>> def publisher(n):
...     time.sleep(1)                                                   #A
...     for i in xrange(n):
...         conn.publish('channel', i)                                  #B
...         time.sleep(1)                                               #B
...
>>> def run_pubsub():
...     threading.Thread(target=publisher, args=(3,)).start()           #D
...     pubsub = conn.pubsub()                                          #E
...     pubsub.subscribe(['channel'])                                   #E
...     count = 0
...     for item in pubsub.listen():                                    #F
...         print item                                                  #G
...         count += 1                                                  #H
...         if count == 4:                                              #H
...             pubsub.unsubscribe()                                    #H
...         if count == 5:                                              #L
...             break                                                   #L
...
>>> run_pubsub()                                                        #C
{'pattern': None, 'type': 'subscribe', 'channel': 'channel', 'data': 1L}#I
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '0'} #J
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '1'} #J
{'pattern': None, 'type': 'message', 'channel': 'channel', 'data': '2'} #J
{'pattern': None, 'type': 'unsubscribe', 'channel': 'channel', 'data':  #K
0L}                                                                     #K
# <end id="pubsub-calls-1"/>
#A We sleep initially in the function to let the SUBSCRIBEr connect and start listening for messages
#B After publishing, we will pause for a moment so that we can see this happen over time
#D Let's start the publisher thread to send 3 messages
#E We'll set up the pubsub object and subscribe to a channel
#F We can listen to subscription messages by iterating over the result of pubsub.listen()
#G We'll print every message that we receive
#H We will stop listening for new messages after the subscribe message and 3 real messages by unsubscribing
#L When we receive the unsubscribe message, we need to stop receiving messages
#C Actually run the functions to see them work
#I When subscribing, we receive a message on the listen channel
#J These are the structures that are produced as items when we iterate over pubsub.listen()
#K When we unsubscribe, we receive a message telling us which channels we have unsubscribed from and the number of channels we are still subscribed to
#END
'''

