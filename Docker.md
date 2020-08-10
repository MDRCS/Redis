## + Bring up Containers

    $ run docker-compose up -d in this directory.

    Run Tests
    docker exec -it python-redis-snippets python voting_articles.py

    Why Using network_mode: "host"?
    Because Redis host defaults to localhost in every redis.Redis(), you would otherwise have to specify host in every occurrence.
