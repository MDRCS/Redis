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


### + Anatomy of a Redis web application :

    Through this chapter, we’ll look at and solve problems that come up in the context of Fake Web Retailer, a fairly large (fake) web store that gets about 100 million hits per day from roughly 5 million unique users who buy more than 100,000 items per day. These numbers are big, but if we can solve big problems easily, then small and medium problems should be even easier. And though these solutions
    target a large web retailer, all but one of them can be handled by a Redis server with no more than a few gigabytes of memory, and are intended to improve performance of a system responding to requests in real time.
    Each of the solutions presented (or some variant of them) has been used to solve real problems in production environments. More specifically, by reducing traditional database load by offloading some processing and storage to Redis, web pages were loaded faster with fewer resources.
    Our first problem is to use Redis to help with managing user login sessions.

    2.1 Login and cookie caching
    Whenever we sign in to services on the internet, such as bank accounts or web mail, these services remember who we are using cookies. Cookies are small pieces of data that websites ask our web browsers to store and resend on every request to that service. For login cookies, there are two common methods of storing login information in cook- ies: a signed cookie or a token cookie.

    + Signed cookies typically store the user’s name, maybe their user ID, when they last logged in, and whatever else the service may find useful. Along with this user-specific information, the cookie also includes a signature that allows the server to verify that the information that the browser sent hasn’t been altered (like replacing the login name of one user with another).
    + Token cookies use a series of random bytes as the data in the cookie. On the server, the token is used as a key to look up the user who owns that token by querying a data- base of some kind. Over time, old tokens can be deleted to make room for new tokens.

- Some pros and cons for both signed cookies and token cookies for referenc- ing information are shown in table 2.1 :

![](./static/pros_cons_cookies.png)

    +++ For the sake of not needing to implement signed cookies, Fake Web Retailer chose to use a token cookie to reference an entry in a relational database table, which stores user login information. By storing this information in the database, Fake Web Retailer can also store information like how long the user has been browsing, or how many items they’ve looked at, and later analyze that information to try to learn how to better market to its users.

    + Bottleneck of writeson relational database :

    As is expected, people will generally look through many different items before choosing one (or a few) to buy, and recording information about all of the different items seen, when the user last visited a page, and so forth, can result in substantial data- base writes. In the long term, that data is useful, but even with database tuning, most relational databases are limited to inserting, updating, or deleting roughly 200–2,000 individual
    rows every second per database server. Though bulk inserts/updates/deletes can be performed faster, a customer will only be updating a small handful of rows for each web page view, so higher-speed bulk insertion doesn’t help here.
    At present, due to the relatively large load through the day (averaging roughly 1,200 writes per second, close to 6,000 writes per second at peak), Fake Web Retailer has had to set up 10 relational database servers to deal with the load during peak hours. It’s our job to take the relational databases out of the picture for login cookies and replace them with Redis.

    To get started, we’ll use a HASH to store our mapping from login cookie tokens to the user that’s logged in. To check the login, we need to fetch the user based on the token and return it, if it’s available. The following listing shows how we check login cookies.

![](./static/check_token.png)

    ++ Checking the token isn’t very exciting, because all of the interesting stuff happens when we’re updating the token itself. For the visit, we’ll update the login HASH for the user and record the current timestamp for the token in the ZSET of recent users. If the user was viewing an item, we also add the item to the user’s recently viewed ZSET and trim that ZSET if it grows past 25 items. The function that does all of this can be seen next.

![](./static/update_token.png)

    +++ And you know what? That’s it. We’ve now recorded when a user with the given session last viewed an item and what item that user most recently looked at. On a server made in the last few years, you can record this information for at least 20,000 item views every second, which is more than three times what we needed to perform against the database. This can be made even faster, which we’ll talk about later. But even for this version,
        we’ve improved performance by 10–100 times over a typical relational data- base in this context.


    Over time, memory use will grow, and we’ll want to clean out old data. As a way of limiting our data, we’ll only keep the most recent 10 million sessions.1 For our cleanup, we’ll fetch the size of the ZSET in a loop. If the ZSET is too large, we’ll fetch the oldest items up to 100 at a time (because we’re using timestamps, this is just the first 100 items in the ZSET), remove them from the recent ZSET, delete the login tokens from the login HASH,
    and delete the relevant viewed ZSETs. If the ZSET isn’t too large, we’ll sleep for one second and try again later. The code for cleaning out old ses- sions is shown next.

    ZCARD key
    Time complexity: O(1)

    Returns the sorted set cardinality (number of elements) of the sorted set stored at key.

    +++ Scaling a simple algorithm :

    How could something so simple scale to handle five million users daily? Let’s check the numbers.
    If we expect five million unique users per day, then in two days (if we always get new users every day),
    we’ll run out of space and will need to start deleting tokens. In one day there are 24 x 3600 = 86,400 seconds,
    so there are 5 million / 86,400 < 58 new sessions every second on average.
    If we ran our cleanup function every second (as our code implements),
    we’d clean up just under 60 tokens every second. But this code can actually clean up more than 10,000 tokens per second across a network,
    and over 60,000 tokens per second locally, which is 150–1,000 times faster than we need.

    - Another solution | EXPIRE :
    -- EXPIRING DATA IN REDIS As you learn more about Redis, you’ll likely discover that some of the solutions we present aren’t the only ways to solve the prob- lem. In this case, we could omit the recent ZSET,
       store login tokens as plain key-value pairs, and use Redis EXPIRE to set a future date or time to clean out both sessions and our recently viewed ZSETs. But using EXPIRE prevents us from explicitly limiting
       our session information to 10 million users, and pre- vents us from performing abandoned shopping cart analysis during session expiration, if necessary in the future.

    2.2 Shopping carts in Redis

    The use of shopping cart cookies is common, as is the storage of the entire cart itself in the cookie. One huge advantage to storing shopping carts in cookies is that you don’t need to write to a database to keep them.
    But one of the disadvantages is that you also need to keep reparsing and validating the cookie to ensure that it has the proper format and contains items that can actually be purchased. Yet another disad- vantage is that
    cookies are passed with every request, which can slow down request sending and processing for large cookies.

    Because we’ve had such good luck with session cookies and recently viewed items, we’ll push our shopping cart information into Redis. Since we’re already keeping user session cookies in Redis (along with recently viewed items),
    we can use the same cookie ID for referencing the shopping cart.
    The shopping cart that we’ll use is simple: it’s a HASH that maps an item ID to the quantity of that item that the customer would like to purchase. We’ll have the web application handle validation for item count, so we only need
    to update counts in the cart as they change. If the user wants more than 0 items, we add the item(s) to the HASH (replacing an earlier count if it existed). If not, we remove the entry from the hash. Our add_to_cart() function can be seen in this listing.

    We now have both sessions and the shopping cart stored in Redis, which helps to reduce request size, as well as allows the performing of statistical calculations on visi- tors to our site based on what items they looked at, what items ended up in their shop- ping carts,
    and what items they finally purchased. All of this lets us build (if we want to) features similar to many other large web retailers: “People who looked at this item ended up buying this item X% of the time,” and “People who bought this item also bought these other items.”
    This can help people to find other related items, which is ultimately good for business.
    With both session and shopping cart cookies in Redis, we now have two major pieces for performing useful data analysis. Continuing on, let’s look at how we can fur- ther reduce our database and web front-end load with caching.

    - Web page caching :

    When producing web pages dynamically, it’s common to use a templating language to simplify page generation. Gone are the days when each page would be written by hand. Modern web pages are generated from page templates with headers, footers, side menus, toolbars, content areas, and maybe even generated JavaScript.
    Despite being capable of dynamically generating content, the majority of pages that are served on Fake Web Retailer’s website don’t change much on a regular basis. Sure, some new items are added to the catalog, old items are removed, sometimes there are specials, and sometimes there are even “hot items” pages.
    But really, only a handful of account settings, past orders, shopping cart/checkout, and similar pages have content that needs to be generated on every page load.
    By looking at their view numbers, Fake Web Retailer has determined that 95% of the web pages that they serve change at most once per day, and don’t actually require content to be dynamically generated. It’s our job to stop generating 95% of pages for every load. By reducing the amount of time we spend generating static content, we
    can reduce the number of servers necessary to handle the same load, and we can serve our site faster. (Research has shown that reducing the time users spend waiting for pages to load increases their desire to use a site and improves how they rate the site.)
    All of the standard Python application frameworks offer the ability to add layers that can pre- or post-process requests as they’re handled. These layers are typically called middleware or plugins. Let’s create one of these layers that calls out to our Redis caching function. If a web request can’t be cached, we’ll generate the page
    and return the con- tent. If a request can be cached, we’ll try to fetch and return the page from the cache; otherwise we’ll generate the page, cache the result in Redis for up to 5 minutes, and return the content. Our simple caching method can be seen in the next listing.

![](./static/cache_request.png)

    For that 95% of content that could be cached and is loaded often, this bit of code removes the need to dynamically generate viewed pages for 5 minutes. Depending on the complexity of content, this one change could reduce the latency for a data-heavy page from maybe 20–50ms, down to one round trip to Redis (under 1ms for a local connection,
    under 5ms for computers close to each other in the same data center). For pages that used to hit the database for data, this can further reduce page load time and database load.
    Now that we’ve cut loading time for pages that don’t change often, can we keep using Redis to cut loading time for pages that do change often? Of course we can! Keep reading to find out how.


    2.4 Database row caching
    In this chapter so far, we’ve moved login and visitor sessions from our relational data- base and web browser to Redis, we’ve taken shopping carts out of the relational data- base and put them into Redis, and we’ve cached entire pages in Redis. This has helped us improve performance and reduce the load on our relational database, which has also lowered our costs.


    Individual product pages that we’re displaying to a user typically only load one or two rows from the database: the user information for the user who’s logged in (with our generated pages, we can load that with an AJAX call to keep using our cache), and the information about the item itself. Even for pages where we may not want to cache the whole page
    (customer account pages, a given user’s past orders, and so on), we could instead cache the individual rows from our relational database.
    As an example of where caching rows like this would be useful, let’s say that Fake Web Retailer has decided to start a new promotion to both clean out some older inventory and get people coming back to spend money. To make this happen, we’ll start performing daily deal sales for certain items until they run out. In the case of a deal, we can’t
    cache the full page, because then someone might see a version of the page with an incorrect count of items remaining. And though we could keep reading the item’s row from the database, that could push our database to become over- utilized, which would then increase our costs because we’d need to scale our data- bases up again.

    To cache database rows in preparation for a heavy load, we’ll write a daemon func- tion that will run continuously, whose purpose will be to cache specific database rows in Redis, updating them on a variable schedule. The rows themselves will be JSON- encoded dictionaries stored as a plain Redis value. We’ll map column names and row values to the dictionary keys and values. An

    example row can be seen in figure 2.1.
    In order to know when to update the cache, we’ll use two ZSETs. Our first ZSET, the sched- uleZSET, will use the row ID from the original database row as the member of the ZSET. We’ll use a timestamp for our schedule scores, which will tell us when the row should be copied to Redis next. Our second ZSET, the delayZSET, will use the same row ID for the members, but the score
    will be how many seconds to wait between cache updates.

![](./static/database_rows.png)

    In order for rows to be cached on a regular basis by the caching function, we’ll first add the row ID to our delay ZSET with the given delay. This is because our actual cach- ing function will require the delay, and if it’s missing, will remove the scheduled item. When the row ID is in the delay ZSET, we’ll then add the row ID to our schedule ZSET with the current timestamp.
    If we want to stop a row from being synced to Redis and remove it from the cache, we can set the delay to be less than or equal to 0, and our caching function will handle it. Our function to schedule or stop caching can be seen in the following listing.

    def schedule_row_cache(conn, row_id, delay):
        conn.zadd('delay:', row_id, delay)
        conn.zadd('schedule:', row_id, time.time())

    Now that we have the scheduling part done, how do we cache the rows? We’ll pull the first item from the schedule ZSET with its score. If there are no items, or if the time- stamp returned is in the future, we’ll wait 50 milliseconds and try again. When we have an item that should be updated now, we’ll check the row’s delay. If the delay for the next caching time is less than or
    equal to 0, we’ll remove the row ID from the delay and schedule ZSETs, as well as delete the cached row and try again. Finally, for any row that should be cached, we’ll update the row’s schedule, pull the row from the data- base, and save a JSON-encoded version of the row to Redis. Our function for doing this can be seen in this listing.

    With the combination of a scheduling function and a continuously running caching function, we’ve added a repeating scheduled autocaching mechanism. With these two functions, inventory rows can be updated as frequently as we think is reasonable. For a daily deal with inventory counts being reduced and affecting whether someone can buy the item, it probably makes sense to update
    the cached row every few seconds if there are many buyers. But if the data doesn’t change often, or when back-ordered items are acceptable, it may make sense to only update the cache every minute. Both are possible with this simple method.

    2.5 Web page analytics :

    As people come to the websites that we build, interact with them, maybe even pur- chase something from them, we can learn valuable information. For example, if we only pay attention to pages that get the most views, we can try to change the way the pages are formatted, what colors are being used, maybe even change what other links are shown on the pages. Each one of these changes can
    lead to a better or worse expe- rience on a page or subsequent pages, or even affect buying behavior.

    + The line we need to add to update_token() :

    -> conn.zincrby('viewed:', item, -1)

    With this one line added, we now have a record of all of the items that are viewed. Even more useful, that list of items is ordered by the number of times that people have seen the items, with the most-viewed item having the lowest score, and thus hav- ing an index of 0. Over time, some items will be seen many times and others rarely. Obviously we only want to cache commonly seen items,
    but we also want to be able to discover new items that are becoming popular, so we know when to cache them.

    To keep our top list of pages fresh, we need to trim our list of viewed items, while at the same time adjusting the score to allow new items to become popular. You already know how to remove items from the ZSET from section 2.1, but rescaling is new. ZSETs have a function called ZINTERSTORE, which lets us combine one or more ZSETs and mul- tiply every score in the input ZSETs by a given number.
    (Each input ZSET can be multi- plied by a different number.) Every 5 minutes, let’s go ahead and delete any item that isn’t in the top 20,000 items, and rescale the view counts to be half has much as they were before. The following listing will both delete items and rescale remaining scores.

![](./static/can_cache_update.png)

    ++ With the rescaling and the counting, we now have a constantly updated list of the most-frequently viewed items at Fake Web Retailer. Now all we need to do is to update our can_cache() function to take into consideration our new method of deciding whether a page can be cached, and we’re done. You can see our new can_cache() function here.

![](./static/rescale_viewed.png)

![](./static/can_cache_update.png)

    - IMPORTANT, Summary :

    +++ And with that final piece, we’re now able to take our actual viewing statistics and only cache those pages that are in the top 10,000 product pages. If we wanted to store even more pages with minimal effort, we could compress the pages before storing them in Redis, use a technology called edge side includes to remove parts of our pages, or we could pre-optimize our templates
        to get rid of unnecessary whitespace. Each of these techniques and more can reduce memory use and increase how many pages we could store in Redis, all for additional performance improvements as our site grows.
