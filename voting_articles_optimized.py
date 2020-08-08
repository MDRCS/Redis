import threading
import time
import unittest

import redis

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25

"""
Exercise: Removing of race conditions
One of the primary purposes of MULTI/EXEC transactions is removing what are known as race conditions, which you saw exposed in listing 3.13. It turns out that the article_vote() function from chapter 1 has a race condition and a second related bug. The race condition can cause a memory leak, and the bug can cause a
vote to not be counted correctly. The chances of either of them happening is very small, but can you spot and fix them? Hint: If you’re having difficulty finding the memory leak, check out section 6.2.5 while consulting the post_article() function.

Exercise: Improving performance
A secondary purpose of using pipelines in Redis is to improve performance (we’ll talk more about this in sections 4.4–4.6). In particular, by reducing the number of round trips between Redis and our client that occur over a sequence of commands, we can significantly reduce the amount of time our client is waiting for a response.
In the get_articles() function we defined in chapter 1, there will actually be 26 round trips between Redis and the client to fetch a full page of articles. This is a waste. Can you change get_articles() so that it only makes two round trips?

Exercise: Replacing timestamp ZSETs with EXPIRE
In sections 2.1, 2.2, and 2.5, we used a ZSET with timestamps to keep a listing of session IDs to clean up. By using this ZSET, we could optionally perform analytics over our items when we cleaned sessions out. But if we aren’t interested in analytics, we can instead get similar semantics with expiration, without needing a cleanup func- tion.
Can you update the update_token() and add_to_cart() functions to expire keys instead of using a “recent” ZSET and cleanup function?
"""


# <start id="exercise-fix-article-vote"/>
def article_vote(conn, user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    posted = conn.zscore('time:', article)  # A
    if posted < cutoff:
        return

    article_id = article.partition(':')[-1]
    pipeline = conn.pipeline()
    pipeline.sadd('voted:' + article_id, user)
    pipeline.expire('voted:' + article_id, int(posted - cutoff))  # B
    if pipeline.execute()[0]:
        pipeline.zincrby('score:', article, VOTE_SCORE)  # C
        pipeline.hincrby(article, 'votes', 1)  # C
        pipeline.execute()  # C


# <end id="exercise-fix-article-vote"/>
# A If the article should expire bewteen our ZSCORE and our SADD, we need to use the posted time to properly expire it
# B Set the expiration time if we shouldn't have actually added the vote to the SET
# C We could lose our connection between the SADD/EXPIRE and ZINCRBY/HINCRBY, so the vote may not count, but that is better than it partially counting by failing between the ZINCRBY/HINCRBY calls
# END

def article_vote(conn, user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    posted = conn.zscore('time:', article)
    article_id = article.partition(':')[-1]
    voted = 'voted:' + article_id

    pipeline = conn.pipeline()
    while posted > cutoff:
        try:
            pipeline.watch(voted)
            if not pipeline.sismember(voted, user):
                pipeline.multi()
                pipeline.sadd(voted, user)
                pipeline.expire(voted, int(posted - cutoff))
                pipeline.zincrby('score:', article, VOTE_SCORE)
                pipeline.hincrby(article, 'votes', 1)
                pipeline.execute()
            else:
                pipeline.unwatch()
            return
        except redis.exceptions.WatchError:
            cutoff = time.time() - ONE_WEEK_IN_SECONDS


# <start id="exercise-fix-get_articles"/>
def get_articles(conn, page, order='score:'):
    start = max(page - 1, 0) * ARTICLES_PER_PAGE
    end = start + ARTICLES_PER_PAGE - 1

    ids = conn.zrevrangebyscore(order, start, end)

    pipeline = conn.pipeline()
    all(map(pipeline.hgetall, ids))  # A

    articles = []
    for id, article_data in zip(ids, pipeline.execute()):  # B
        article_data['id'] = id
        articles.append(article_data)

    return articles


# <end id="exercise-fix-get_articles"/>
# A Prepare the HGETALL calls on the pipeline
# B Execute the pipeline and add ids to the article
# END

# <start id="exercise-no-recent-zset"/>
THIRTY_DAYS = 30 * 86400


def check_token(conn, token):
    return conn.get('login:' + token)  # A


def update_token(conn, token, user, item=None):
    conn.setex('login:' + token, user, THIRTY_DAYS)  # B
    key = 'viewed:' + token
    if item:
        conn.lrem(key, item)
        conn.rpush(key, item)
        conn.ltrim(key, -25, -1)
        conn.zincrby('viewed:', item, -1)
    conn.expire(key, THIRTY_DAYS)  # C


def add_to_cart(conn, session, item, count):
    key = 'cart:' + session
    if count <= 0:
        conn.hrem(key, item)
    else:
        conn.hset(key, item, count)
    conn.expire(key, THIRTY_DAYS)  # D
# <end id="exercise-no-recent-zset"/>
# A We are going to store the login token as a string value so we can EXPIRE it
# B Set the value of the the login token and the token's expiration time with one call
# C We can't manipulate LISTs and set their expiration at the same time, so we must do it later
# D We also can't manipulate HASHes and set their expiration times, so we again do it later
# END
