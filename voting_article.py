import time

# <start id="upvote-code"/>
ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432  # how we got this number is by deviding

"""
Redis data structures that we used are are :

- zset (ordered set) for score:article and time:article
- set for article:users
"""


def article_vote(conn, user, article, vote='up'):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    if conn.zscore('time:', article) < cutoff:  # if the article is oldest than one week you cannot update it 's score
        return

    article_id = article.partition(':')[-1]
    if conn.sadd('voted:' + article_id, user):  # if the article ever was voted by this user
        if vote == 'up':
            conn.zincrby('score:', VOTE_SCORE, article)  # increment ZSET of this article by VOTE_SCORE
        conn.zdecrby('score:', VOTE_SCORE, article)  # increment ZSET of this article by VOTE_SCORE
        conn.hincrby(article, 'votes', 1)


# <end id="upvote-code"/>

# <start id="post-article-code"/>
def post_article(conn, user, title, link):
    article_id = str(conn.incr('article:'))  # increment article_id by one tp get a new unused id

    # set user who have upvoted this article (the poster)
    voted = 'voted:' + article_id
    conn.sadd(voted, user)
    conn.expire(voted, ONE_WEEK_IN_SECONDS)

    # store the new article in the hash.
    now = time.time()
    article = 'article:' + article_id
    conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1,
    })

    # add score and time on zsets for score:article and time:article
    conn.zadd('score:', {article: now + VOTE_SCORE})
    conn.zadd('time:', {article: now})

    return article_id


# <end id="post-article-code"/>

ARTICLES_PER_PAGE = 25


def get_articles(conn, page, order='score:'):
    start = (page - 1) * ARTICLES_PER_PAGE
    end = start + ARTICLES_PER_PAGE - 1

    ids = conn.zrevrange(order, start, end)
    articles = []
    for id in ids:
        article_data = conn.hgetall(id)
        article_data['id'] = id
        articles.append(article_data)

    return articles


# <start id="add-remove-groups"/>
def add_remove_groups(conn, article_id, to_add=[], to_remove=[]):
    article = 'article:' + article_id
    for group in to_add:
        conn.sadd('group:' + group, article)
    for group in to_remove:
        conn.srem('group:' + group, article)


# <end id="add-remove-groups"/>

# <start id="fetch-articles-group"/>
def get_group_articles(conn, group, page, order='score:'):
    key = order + group
    if not conn.exists(key):
        conn.zinterstore(key,
            ['group:' + group, order],
            aggregate='max',
        )
        conn.expire(key, 60)
    return get_articles(conn, page, key)
# <end id="fetch-articles-group"/>

