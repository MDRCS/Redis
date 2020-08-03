# Redis - in-memory database :

    - Story behind Creation of Redis :

    Redis was created about three years ago for practical reasons: basically, I was trying to do the impossible with an on-disk SQL database. I was handling a large write-heavy load with the only hardware I was able to afford—a little virtualized instance.
    My problem was conceptually simple: my server was receiving a stream of page views from multiple websites using a small JavaScript tracker. I needed to store the lat- est n page views for every site and show them in real time to users connected to a web interface,
    while maintaining a small history.

    With a peak load of a few thousand page views per second, whatever my database schema was, and whatever trade-offs I was willing to pick, there was no way for my SQL store to handle the load with such poor hardware. My inability to upgrade the hard- ware for cost
    concerns coupled with the feeling that to handle a capped list of values shouldn’t have been so hard, after all, gave me the idea of creating a throw-away pro- totype of an in-memory data store that could handle lists as a native data type, with constant-time pop
    and push operations on both sides of the lists. To make a long story short, the concept worked, I rewrote the first prototype using the C language, added a fork-based persistence feature, and Redis was born.


    - Author is first use of Redis :

    + My first experience with Redis was at a company that needed to search a data- base of client contacts. The search needed to find contacts by name, email address, location, and phone number. The system was written to use a SQL database that performed a series of queries
      that would take 10–15 seconds to find matches among 60,000 clients. After spending a week learning the basics of what was available in Redis, I built a search engine that could filter and sort on all of those fields and more, returning responses within 50 milliseconds.

    - Setting-up Redis on MacOS :
    $ brew install redis

    $ redis-server
    $ redis-server /usr/local/etc/redis.conf

    What is Redis?
    When I say that Redis is a database, I’m only telling a partial truth. Redis is a very fast non-relational database that stores a mapping of keys to five different types of values. Redis supports in-memory persistent storage on disk, replication to scale read perfor- mance,
    and client-side sharding1 to scale write performance. That was a mouthful, but I’ll break it down by parts.

    - It’s not uncommon to hear Redis compared to memcached, which is a very high- performance, key-value cache server. Like memcached, Redis can also store a mapping of keys to values and can even achieve similar performance levels as memcached.

    + Generally speaking, many Redis users will choose to store data in Redis only when the performance or functionality of Redis is necessary, using other relational or non-relational data storage for data where slower performance is accept- able, or where data
    is too large to fit in memory economically.

    When using an in-memory database like Redis, one of the first questions that’s asked is “What happens when my server gets turned off?” Redis has two different forms of per- sistence available for writing in-memory data to disk in a compact format. The first method is a
    point-in-time dump either when certain conditions are met (a number of writes in a given period) or when one of the two dump-to-disk commands is called. The other method uses an append-only file that writes every command that alters data in Redis to disk as it happens.
    Depending on how careful you want to be with your data, append-only writing can be configured to never sync, sync once per second, or sync at the completion of every operation.

    Even though Redis is able to perform well, due to its in-memory design there are situations where you may need Redis to process more read queries than a single Redis server can handle. To support higher rates of read performance (along with handling failover if the server
    that Redis is running on crashes), Redis supports master/slave replication where slaves connect to the master and receive an initial copy of the full database. As writes are performed on the master, they’re sent to all connected slaves for updating the slave datasets in real time.
    With continuously updated data on the slaves, clients can then connect to any slave for reads instead of making requests to the master.

    - writes to Redis data are always fast, because data is always in memory, and queries to Redis don’t need to go through a typical query parser/optimizer.

    ! Redis - Use case :

    + By using Redis instead of a relational or other primarily on-disk database, you can avoid writing unnecessary temporary data, avoid needing to scan over and delete this temporary data, and ultimately improve performance. These are both simple exam- ples, but they demonstrate how your choice of tool can greatly affect the way you solve your problems.
    - As you continue to read about Redis, try to remember that almost everything that we do is an attempt to solve a problem in real time

    1.2 What Redis data structures look like :
    - Redis allows us to store keys that map to any one of five different data structure types; STRINGs, LISTs, SETs, HASHes, and ZSETs. Each of the five differ- ent structures have some shared commands (DEL, TYPE, RENAME, and others), as well as some commands that can only be used by one or two of the structures

![](./static/data_structures.png)

    - Set-up python env :

    $ sudo python -m easy_install redis hiredis (hiredis is an optional performance-improving C library).

    1- Strings in Redis :

    $ redis-cli # start cli of redis
    - with String datatype We can GET values, SET values, and DEL values.

![](./static/ops.png)
![](./static/example_string.png)

    2- Lists in Redis :

    The operations that can be performed
    on LISTs are typical of what we find in
    almost any programming language. We
    can push items to the front and the back
    of the LIST with LPUSH/RPUSH; we can pop
    items from the front and back of the list
    with LPOP/RPOP; we can fetch an item at a given position with LINDEX; and we can fetch a range of items with LRANGE.

    - Example :

    redis-cli> rpush list-key item-0
    redis-cli> rpush list-key item-1
    redis-cli> rpush list-key item-2
    redis-cli> lrange list-key 0 -1
    redis-cli> lindex list-key 1
    redis-cli> lpop list-key
    redis-cli> lrange list-key 0 -1

    3- Sets in Redis :

    Redis SETs are unordered,
    we can’t push and pop items from the
    ends like we did with LISTs. Instead, we
    add and remove items by value with the SADD and SREM commands. We can also find out whether an item is in the SET quickly with SISMEMBER, or fetch the entire set with SMEMBERS (this can be slow for large SETs, so be careful).

![](./static/SET_OPS.png)
![](./static/example_set.png)

    - As you can probably guess based on the STRING and LIST sections, SETs have many other uses beyond adding and removing items. Three commonly used operations with SETs include intersection, union, and difference (SINTER, SUNION, and SDIFF, respec- tively).

    4- Hashes in Redis :

![](./static/hashes.png)
![](./static/example_hashes.png)

    5- Sorted sets or ZSET in Redis :

![](./static/ZSET.png)

    - Redis use case : Voting on articles

      First, let’s start with some numbers and limitations on our problem, so we can solve the problem without losing sight of what we’re trying to do. Let’s say that 1,000 articles are submitted each day. Of those 1,000 articles, about 50 of them are interesting
      enough that we want them to be in the top-100 articles for at least one day. All of those 50 articles will receive at least 200 up votes. We won’t worry about down votes for this version.

    + Reddit, a site that offers the ability to vote on articles.
    + Stack Overflow, a site that offers the ability to vote on questions.

    - Solution :

    When dealing with scores that go down over time, we need to make the posting time, the current time, or both relevant to the overall score. To keep things simple, we’ll say that the score of an item is a function of the time that the article was posted, plus a constant multiplier times the number of votes that the article has received.
    The time we’ll use the number of seconds since January 1, 1970, in the UTC time zone, which is commonly referred to as Unix time. We’ll use Unix time because it can be fetched easily in most programming languages and on every platform that we may use Redis on. For our constant, we’ll take the
    number of seconds in a day (86,400) divided by
    the number of votes required (200) to last a full
    day, which gives us 432 “points” added to the
    score per vote.
    To actually build this, we need to start thinking of structures to use in Redis. For starters, we need to store article information like the title, the link to the article, who posted it, the time it was posted, and the number of votes received. We can use a Redis HASH to store this information, and an example article can be seen in figure 1.8.

![](./static/article.png)

    To store a sorted set of articles themselves, we’ll use a ZSET, which keeps items ordered by the item scores. We can use our article ID as the member, with the ZSET score being the article score itself. While we’re at it, we’ll create another ZSET with the score being just the times that the articles were posted, which gives us an option of browsing
    arti- cles based on article score or time. We can see a small example of time- and score- ordered article ZSETs in figure 1.9.

![](./static/ZSET_TIME_SCORE.png)

    In order to prevent users from voting for the same article more than once, we need to store a unique listing of users who have voted for each article. For this, we’ll use a SET for each article, and store the member IDs of all users who have voted on the given article. An example SET of users who have voted on an article is shown in figure 1.10.
    For the sake of memory use over time, we’ll say that after a week users can no lon- ger vote on an article and its score is fixed. After that week has passed, we’ll delete the SET of users who have voted on the article.
    Before we build this, let’s take a look at what would happen if user 115423 were to vote for article 100408 in figure 1.11.
    Now that you know what we’re going to build, let’s build it! First, let’s handle voting. When someone tries to vote on an article, we first verify that the article was posted within the last week by checking the article’s post time with ZSCORE. If we still have time, we then try to add the user to the article’s voted SET

![](./static/articles_voted_users.png)
![](./static/voting_ops.png)

    with SADD. Finally, if the user didn’t previously vote on that article, we increment the score of the article by 432 (which we calculated earlier) with ZINCRBY (a command that increments the score of a member), and update the vote count in the HASH with HINCRBY (a command that increments a value in a hash).

    article_vote.py -> Redis In order to be correct, technically our SADD, ZINCRBY, and HINCRBY calls should be in a transaction. But since we don’t cover transac-
    tions until chapter 4, we won’t worry about them for now.

    3.2 Posting and fetching articles
    To post an article, we first create an article ID by incrementing a counter with INCR. We then create the voted SET by adding the poster’s ID to the SET with SADD. To ensure that the SET is removed after one week, we’ll give it an expiration time with the EXPIRE command, which lets Redis automatically delete it. We then store the article informa- tion with HMSET.
    Finally, we add the initial score and posting time to the relevant ZSETs with ZADD. We can see the code for posting an article in listing 1.7.

    Okay, so we can vote, and we can post articles. But what about fetching the current top-scoring or most recent articles? For that, we can use ZRANGE to fetch the article IDs, and then we can make calls to HGETALL to fetch information about each article. The only tricky part is that we must remember that ZSETs are sorted in ascending order by their score. But we can
    fetch items based on the reverse order with ZREVRANGEBYSCORE. The function to fetch a page of articles is shown in listing 1.8.

    We can now get the top-scoring articles across the entire site. But many of these article voting sites have groups that only deal with articles of a particular topic like cute ani- mals, politics, programming in Java, and even the use of Redis. How could we add or alter our code to offer these topical groups?

    Grouping articles
    To offer groups requires two steps. The first step is to add information about which articles are in which groups, and the second is to actually fetch articles from a group. We’ll use a SET for each group, which stores the article IDs of all articles in that group. In listing 1.9, we see a function that allows us to add and remove articles from groups.

- Getting the score of an article from a given group :

  When we’re browsing a specific group, we want to be able to see the scores of all of the articles in that group. Or, really, we want them to be in a ZSET so that we can have the scores already sorted and ready for paging over. Redis has a command called ZINTERSTORE, which, when provided with SETs and ZSETs, will find those entries that are in all of the SETs and ZSETs,
  combining their scores in a few different ways (items in SETs are considered to have scores equal to 1). In our case, we want the maximum score from each item (which will be either the article score or when the article was posted, depending on the sorting option chosen).

![](./static/intersection_set_zset.png)


    To visualize what is going on, let’s look at figure 1.12. This figure shows an example ZINTERSTORE operation on a small group of articles stored as a SET with the much larger (but not completely shown) ZSET of scored articles. Notice how only those arti- cles that are in both the SET and the ZSET make it into the result ZSET?
    To calculate the scores of all of the items in a group, we only need to make a ZINTERSTORE call with the group and the scored or recent ZSETs. Because a group may be large, it may take some time to calculate, so we’ll keep the ZSET around for 60 sec- onds to reduce the amount of work that Redis is doing. If we’re careful (and we are), we can even use our existing get_articles()
    function to handle pagination and arti- cle data fetching so we don’t need to rewrite it. We can see the function for fetching a page of articles from a group in listing 1.10.

![](./static/get_articles_groups.png)

    On some sites, articles are typically only in one or two groups at most (“all articles” and whatever group best matches the article). In that situation, it would make more sense to keep the group that the article is in as part of the article’s HASH, and add one more ZINCRBY call to the end of our article_vote() function. But in our case, we chose to allow articles to be a part of
    multiple groups at the same time (maybe a pic- ture can be both cute and funny), so to update scores for articles in multiple groups,
    ++ we’d need to increment all of those groups at the same time. For an article in many groups, that could be expensive, so we instead occasionally perform an intersection. How we choose to offer flexibility or limitations can change how we store and update our data in any database, and Redis is no exception.

    Exercise: Down-voting
    In our example, we only counted people who voted positively for an article. But on many sites, negative votes can offer useful feedback to everyone. Can you think of a way of adding down-voting support to article_vote() and post_article()? If pos- sible, try to allow users to switch their votes. Hint: if you’re stuck on vote switching, check out SMOVE, which I introduce briefly in chapter 3.

    NOT: If there’s one concept that you should take away from this chapter, it’s that Redis is another tool that you can use to solve problems.


