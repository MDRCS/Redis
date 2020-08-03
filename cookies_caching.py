import time
import urllib


def to_bytes(x):
    return x.encode() if isinstance(x, str) else x


def to_str(x):
    return x.decode() if isinstance(x, bytes) else x


# <start id="_1311_14471_8266"/>
def check_token(conn, token):
    return conn.hget('login:', token)  # A


# <end id="_1311_14471_8266"/>
# A Fetch and return the given user, if available
# END


# <start id="_1311_14471_8265"/>
def update_token(conn, token, user, item=None):
    timestamp = time.time()  # A
    conn.hset('login:', token, user)  # B
    conn.zadd('recent:', {token: timestamp})  # C
    if item:
        conn.zadd('viewed:' + token, {item: timestamp})  # D
        conn.zremrangebyrank('viewed:' + token, 0, -26)  # E


# <end id="_1311_14471_8265"/>
# A Get the timestamp
# B Keep a mapping from the token to the logged-in user
# C Record when the token was last seen
# D Record that the user viewed the item
# E Remove old items, keeping the most recent 25
# END


# <start id="_1311_14471_8270"/>
QUIT = False
LIMIT = 10000000


def clean_sessions(conn):
    while not QUIT:
        size = conn.zcard('recent:')  # A
        if size <= LIMIT:  # B
            time.sleep(1)  # B
            continue

        end_index = min(size - LIMIT, 100)  # C
        tokens = conn.zrange('recent:', 0, end_index - 1)  # C

        session_keys = []  # D
        for token in tokens:  # D
            token = to_str(token)
            session_keys.append('viewed:' + token)  # D

        conn.delete(*session_keys)  # E
        conn.hdel('login:', *tokens)  # E
        conn.zrem('recent:', *tokens)  # E


# <end id="_1311_14471_8270"/>
# A Find out how many tokens are known
# B We are still under our limit, sleep and try again
# C Fetch the token ids that should be removed
# D Prepare the key names for the tokens to delete
# E Remove the oldest tokens
# END

"""

How could something so simple scale to handle five million users daily? Let’s check the numbers.
If we expect five million unique users per day, then in two days (if we always get new users every day),
we’ll run out of space and will need to start deleting tokens. In one day there are 24 x 3600 = 86,400 seconds,
so there are 5 million / 86,400 < 58 new sessions every second on average.
If we ran our cleanup function every second (as our code implements),
we’d clean up just under 60 tokens every second. But this code can actually clean up more than 10,000 tokens per second across a network,
and over 60,000 tokens per second locally, which is 150–1,000 times faster than we need.

"""


# <start id="_1311_14471_8279"/>
def add_to_cart(conn, session, item, count):
    if count <= 0:
        conn.hrem('cart:' + session, item)  # A
    else:
        conn.hset('cart:' + session, item, count)  # B


# <end id="_1311_14471_8279"/>
# A Remove the item from the cart
# B Add the item to the cart
# END


# <start id="_1311_14471_8271"/>
def clean_full_sessions(conn):
    while not QUIT:
        size = conn.zcard('recent:')
        if size <= LIMIT:
            time.sleep(1)
            continue

        end_index = min(size - LIMIT, 100)
        sessions = conn.zrange('recent:', 0, end_index - 1)

        session_keys = []
        for sess in sessions:
            sess = to_str(sess)
            session_keys.append('viewed:' + sess)
            session_keys.append('cart:' + sess)  # A

        conn.delete(*session_keys)
        conn.hdel('login:', *sessions)
        conn.zrem('recent:', *sessions)


# <end id="_1311_14471_8271"/>
# A The required added line to delete the shopping cart for old sessions
# END

# --------------- Below this line are helpers to test the code ----------------

def extract_item_id(request):
    parsed = urllib.parse.urlparse(request)
    query = urllib.parse.parse_qs(parsed.query)
    return (query.get('item') or [None])[0]


def is_dynamic(request):
    parsed = urllib.parse.urlparse(request)
    query = urllib.parse.parse_qs(parsed.query)
    return '_' in query


def hash_request(request):
    return str(hash(request))


# <start id="_1311_14471_8289"/>
def can_cache(conn, request):
    item_id = extract_item_id(request)  # A
    if not item_id or is_dynamic(request):  # B
        return False
    rank = conn.zrank('viewed:', item_id)  # C
    return rank is not None and rank < 10000  # D


# <end id="_1311_14471_8289"/>
# A Get the item id for the page, if any
# B Check whether the page can be statically cached, and whether this is an item page
# C Get the rank of the item
# D Return whether the item has a high enough view count to be cached
# END

# <start id="_1311_14471_8291"/>
def cache_request(conn, request, callback):
    if not can_cache(conn, request):  # A
        return callback(request)  # A

    page_key = 'cache:' + hash_request(request)  # B
    content = conn.get(page_key)  # C

    if not content:
        content = callback(request)  # D
        conn.setex(page_key, 300, content)  # E

    return content  # F
# <end id="_1311_14471_8291"/>
# A If we cannot cache the request, immediately call the callback
# B Convert the request into a simple string key for later lookups
# C Fetch the cached content if we can, and it is available
# D Generate the content if we can't cache the page, or if it wasn't cached
# E Cache the newly generated content if we can cache it
# F Return the content
# END
