Pygmy
=====

[![Requirements Status](https://requires.io/github/amitt001/pygmy/requirements.svg?branch=master)](https://requires.io/github/amitt001/pygmy/requirements/?branch=master)  [![Build Status](https://travis-ci.org/amitt001/pygmy.svg?branch=master)](https://travis-ci.org/amitt001/pygmy)

Live version of this project: [https://pygy.co](https://pygy.co)

Open-source, extensible & easy-to-use URL shortener. It's very easy to host and run. It's created keeping in mind that it should be easy to have your custom URL shortener up and running without much effort.

Major features are:
- Custom URL
- Auto expiry URL
- Secret key protected URL
- User Login/Sign up
- User dashboard
- Link Analytics(add + to the tiny URL to get link stats)

The architecture is very loosely coupled which allows custom integrations very easily.

The project has 3 major parts:
- The core program for URL shortening
- REST API on top. Uses Flask framework.
- The UI layer for rendering the UI. It uses Django framework.

Each part is independent of other part and it can function independently.

Tech Stack:

Python 3, Javascript, JQuery, HTML, CSS
REST API: Flask
Pyui: Django(It provides a web user interface.)
DB: PostgreSQL/MySQL/SQLite


Setup:
======

- Clone `git clone https://github.com/amitt001/pygmy.git & cd pygmy`
- Install pip `easy_install pip` or `apt-get install python3-pip`
- Install virtualenv (optional but recommended)
    - `pip install virtualenv`
    - `virtualenv env`
    - `source env/bin/activate`
- Install dependencies `pip install -r requirements.txt` (if you are using MySQL or PostgreSQL check db setup section)
- cd src
- To run the rest api `./run` to run UI `python pyui/manage.py runserver 127.0.0.1:8000`
- Visit 127.0.0.1:8000 to use the app

Note:
1. The project has two config files:
    - pygmy.cfg: src/pygmy/config/pygmy.cfg rest API and pygmy core settings file
    - settings.py: src/pyui/pyui/settings.py Django settings file
2. SQLite is default db, if you are using PostgreSQL or MySQL with this project, make sure they are installed into the system.
3. To modify config settings vim src/pygmy/config/pygmy.cfg
4. You can run pygmy shell present in src directory to run the program on terminal
5. By default src/pyui/pyui/settings.py DEBUG is set to True set it to False in production


Using API
=========

Create User:

    curl -XPOST http://127.0.0.1:9119/api/user/1 -H 'Content-Type: application/json' -d '{
    "email": "00amit99@gmail.com",
    "f_name": "Amit",
    "l_name": "Tripathi",
    "password": "amit@123"
    }'


Get User:

Get All User Link:

Create Link:

Get Link:

How Auth Token Works:
=====================

It uses JWT. When user logs in using username and password a token is generated that are marked as fresh and it has a time period of 30 minutes. After 30 minutes. When a request comes with the old token and a new token is generated from the refresh token API. This refreshed token has a new field `fresh=False`. This new token can only shorten the URL and refresh the token for the further user. It CAN'T reset the password, disable the link and change the secret key of the URL.

DB Setup:
---------

**Use MySQL:**

`pip install pymysql`

Check correct port:

`mysqladmin variables | grep port`

Enter below line in src/pygmy/core/pygmy.cfg fro database->url value

`mysql+pymysql://root:root@127.0.0.1:3306/pygmy`

Enter MySQL URL

`CREATE DATABASE pygmy;`


**Use Postgresql**

`pip install psycopg2`

`postgres://amit@127.0.0.1:5432/pygmy`

Use Sqlite
==========

SQLite is natively supported in Python

`sqlite:////var/lib/pygmy/pygmy.db`

Shell Usage
===========

Open shell using ./pygmy/src/shell. Available context is pygmy, Config, DB, etc. See all context by using pygmy_context.

Shorten a link:

```
In [1]: shorten('http://iamit.xyz')
Out[1]:
{'created_at': '15 Nov, 2017 17:33:42',
 'description': None,
 'expire_after': None,
 'hits_counter': 0,
 'id': 'http://0.0.0.0:9119/api/link/5',
 'is_custom': False,
 'is_disabled': False,
 'is_protected': False,
 'long_url': 'http://iamit.xyz',
 'owner': None,
 'secret_key': '',
 'short_code': 'f',
 'short_url': 'http://pygy.co/f',
 'updated_at': '2017-11-15T17:33:42.772520+00:00'}

In [2]: shorten('http://iamit.xyz', request=1)
Out[2]: <pygmy.model.link.Link at 0x105ca1b70>

In [3]: unshorten('f')
Out[3]:
{'created_at': '15 Nov, 2017 17:33:42',
 'description': None,
 'expire_after': None,
 'hits_counter': 0,
 'id': 'http://0.0.0.0:9119/api/link/5',
 'is_custom': False,
 'is_disabled': False,
 'is_protected': False,
 'long_url': 'http://iamit.xyz',
 'owner': None,
 'secret_key': '',
 'short_code': 'f',
 'short_url': 'http://pygy.co/f',
 'updated_at': '2017-11-15T17:33:42.772520+00:00'}

In [4]: link_stats('f')
Out[4]:
{'country_stats': 0,
 'created_at': datetime.datetime(2017, 11, 15, 17, 33, 42, 772520),
 'long_url': 'http://iamit.xyz',
 'referrer': 0,
 'short_code': 'f',
 'time_series_base': None,
 'time_stats': 0,
 'total_hits': 0}

In [5]: # check available context of the shell
In [6]: pygmy_context

In [7]: # Create custom short URL

In [8]: shorten('http://iamit.xyz', short_code='amit')
Out[8]:
{'long_url': 'http://iamit.xyz',
 'short_code': 'amit',
 'short_url': 'http://pygy.co/amit'}

In [9]: shorten?
Signature: shorten(long_url, short_code=None, expire_after=None, description=None, secret_key=None, owner=None, request=None)
Docstring:
    Helper class that has been delegated the task of inserting the
    passed url in DB, base 62 encoding from DB id and return the short
    URL value.
```

Link stats:
===========

For getting geo location stats from IP maxminds' GeoLite2-Country.mmd database is used. It's in src/pygmy/app folder.

License
=======

The MIT license (MIT)