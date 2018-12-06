====
TODO
====

* Reduce image size from 550+MB to > 200MB

* Complete docker compose setup

* Deploy pygy.co demo website with docker compose

* For same netloc same url, forward stash same url

* If url pattern doesn't match. Show a 404 page

* Remove incode created_at updated_at utc date fro mysql

* Disable url by owner

* Improved cfg read

* Option to commit lazily instead of up front commit

* Alembic migrations

* Add logging

* Make module installable

* On back button remove link options

* On link option fold do not post data

* ALL errors from api should be in json format

* Rest client and shell api should match

* Make PygmyApiClient signleton

* Show expire time left

* Logout automatically on access token and refresh token not found

* Link analytics ( hits done)


Changelog
=========

* Rest api

* UI

* Add cli shell and start support

* Read from pygmy.cfg

* CRC32 hash on the long url and query first on hash then on long url.
  In case user is logged in use hash and username to get result(coz chnaces of collision
  is very low for a user)

* Hits counter logic

* Validation of short code on both rest api and ui level

* If secret generate a new URL even if already exists.

* Protected Link by secret key

* Handle/understand CORS

* JWT based auth

* Link title on mouse hover dashboard

* Add + to url to get stats

- Links Stats

    * Total clicks

    * Country wise clicks

    * Source of clicks from referrer

Deployment Issues:
------------------

SQlite db path not found create dir