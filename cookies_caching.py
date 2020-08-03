import time


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
