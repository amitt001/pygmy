<p align="center"><img src="src/pyui/static/logo/logov2.png" alt="pygmy" height="200px"></p>

Pygmy
=====

[![Build Status](https://travis-ci.org/amitt001/pygmy.svg?branch=master)](https://travis-ci.org/amitt001/pygmy) [![Coverage Status](https://coveralls.io/repos/github/amitt001/pygmy/badge.svg?branch=master)](https://coveralls.io/github/amitt001/pygmy?branch=master) [![Requirements Status](https://requires.io/github/amitt001/pygmy/requirements.svg?branch=master)](https://requires.io/github/amitt001/pygmy/requirements/?branch=master)

Live version of this project @ [https://pygy.co](https://pygy.co)

Check link stats by adding **+** to the URL. Example [pygy.co/pygmy+](https://pygy.co/pygmy+)

# Table of Contents
- [Pygmy](#pygmy)
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Technical Info](#tech-used)
- [Installaton/Setup](#installatonsetup)
- [DB Setup:](#db-setup)
    - [Use MySQL](#use-mysql)
    - [Use Postgresql](#use-postgresql)
    - [Use SQLite](#use-sqlite)
- [Using Pygmy API](#using-pygmy-api)
    - [Create User:](#create-user)
- [Shell Usage](#shell-usage)
- [How Link Stats Are Generated?](#how-link-stats-are-generated)
- [How Pygmy Auth Token Works?](#how-pygmy-auth-token-works)
- [Development](#development)
- [Contributions](#contributions)
- [Sponsorship](#sponsorship)
- [License](#license)

Pygmy or `pygy.co` is an open-source, extensible & easy-to-use but powerful URL shortener. It's created keeping in mind that it should be easy to host and run your custom URL shortener without much effort. [Open-source Python URL shortener]

The architecture is very loosely coupled which allows custom integrations easily.

**The project has 3 major parts**

- The core URL shortening code
- A REST API on top. Uses Flask framework
- The UI layer for rendering the UI. It uses Django framework

Features
========

- URL shortner
- Customized short URL's(ex: `pygy.co/pygmy`)
- Support to create auto expiry URL after sometime.
- Secret key protected URL's
- User Login/Sign up to track shortned URL's and link stats
- User dashboard
- Link Analytics(add + to the tiny URL to get link stats)

Technical Info
==============

- Python 3, Javascript, JQuery, HTML, CSS
- REST API: Flask
- Pyui: Django(It serves the web user interface)
- DB: PostgreSQL/MySQL/SQLite
- Others: SQLAlchmey, JWT

Installaton/Setup
=================

NOTE: **This module only supports Python 3. Make sure pip and virtualenv are both python 3 based versions.**
      **To install Python 3 on Mac: http://docs.python-guide.org/en/latest/starting/install3/osx/**

1. Clone `git clone https://github.com/amitt001/pygmy.git & cd pygmy`
2. (Optional) Install virtualenv (optional but recommended)
    - `virtualenv -p python3 env`
    - `source env/bin/activate`
3. Install dependencies: `pip3 install -r requirements.txt` (if you are using MySQL or PostgreSQL check [DB setup](#db-setup) section)
4. `cd src`
5. `python run.py` (It runs Flask and Django servers using gunicorn)
6. Visit `127.0.0.1:8000` to use the app

Note:

1. The project has two config files:
    - pygmy.cfg: `src/pygmy/config/pygmy.cfg` rest API and pygmy core settings file
    - settings.py: `src/pyui/pyui/settings.py` Django settings file
2. SQLite is default db, if you are using PostgreSQL or MySQL with this project, make sure they are installed into the system.
3. To modify config settings vim `src/pygmy/config/pygmy.cfg`
4. You can run pygmy shell present in src directory to run the program on terminal. `python shell`
5. By default in `src/pyui/pyui/settings.py` DEBUG is set to True, set it to False in production

DB Setup:
=========

Use MySQL
---------

First install `pymysql`:

`pip install pymysql`

Check correct port:

`mysqladmin variables | grep port`

Change below line in `src/pygmy/core/pygmy.cfg`:

```
engine: mysql
url: mysql+pymysql://root:root@127.0.0.1:3306/pygmy
```

Enter MySQL URL

`CREATE DATABASE pygmy;`

Note: Better using Mysql with version > `5.6.5` to use default value of `CURRENT_TIMESTAMP` for `DATETIME`.

Use Postgresql
--------------

`pip install psycopg2`

`postgres://amit@127.0.0.1:5432/pygmy`

Use SQLite
----------

SQLite is natively supported in Python

`sqlite:////var/lib/pygmy/pygmy.db`

Using Pygmy API
===============

Create User:
------------

    curl -XPOST http://127.0.0.1:9119/api/user/1 -H 'Content-Type: application/json' -d '{
    "email": "amit@gmail.com",
    "f_name": "Amit",
    "l_name": "Tripathi",
    "password": "a_safe_one"
    }'


Get User:

Get All User Link:

Create Link:

Get Link:

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

How Link Stats Are Generated?
=============================

For getting geo location stats from IP maxminds' [GeoLite2-Country.mmd](http://pygy.co/cm) database is used. It's in `src/pygmy/app` directory.

How Pygmy Auth Token Works?
===========================

It uses JWT. When user logs in using username and password two tokens are generated, refresh token and auth token. Auth token is used for authentication with the Pygmy API. Refresh token can only be used to generate new auth token. Auth token has a very short TTL but refresh token has a longer TTL. After 30 minutes. When a request comes with the old auht token and a new token is generated from the refresh token API. User passwords are encrypted by [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) hash algorithm.

Development
===========

Run tests and generate a coverage report:

`coverage run --source src/pygmy -m py.test`

See coverage report:

`coverage report`

Contributions
=============

Thanks [batarian71](https://github.com/batarian71) for providing the logo icon.

Sponsorship
===========

I would like to thank DigitalOcean for providing initial hosting to Pygmy project. Pygy.co is hosted on DigitalOcean.

<a href="https://www.digitalocean.com/"><img src="https://i.imgur.com/6cYodyH.png"></a>

License
=======

The MIT license (MIT)

[Read License Terms](https://github.com/amitt001/pygmy/blob/master/LICENSE)
