Pygmy
=====

Live version of this project: [https://pygy.co](https://pygy.co)

Open-source, extensible & easy-to-use URL shortener. Pygmy is a feature-rich, easy-to-use, extensible and easy to deploy and host url shortener. It's created keeping in mind that it should be easy to deploy and extend.

Major Features:
- Custom URL
- Auto expiry URL
- Secret key protected URL
- User Login/Sign up
- User dashboard
- Link Analytics(add + to the tiny URL to get link stats)

This is one of the most powerful, feature-rich open-source URL shortener available. The architecture is very loosely coupled which allows custom integrations very easily.
The project has 3 major parts:
- The core program for URL shortening
- REST API on top. Uses Flask framework.
- The UI layer for rendering the UI. It uses Django framework.

Each part is independent of other part and it can function independently. The project is created keeping in mind that each of the parts can be used separately without any dependency on other part.
Its written in Python 3 and it doesn't support/not tested with python 2

Setup:
======

- Clone `git clone https://github.com/amitt001/pygmy.git & cd pygmy`
- Install pip `easy_install pip` or `apt-get install python3-pip`
- Install virtualenv (optional but recommended)
    - `pip install virtualenv`
    - `virtualenv env`
    - `source env/bin/activate`
- Install dependencies `pip install -r requirements.txt` (if you are using mysql or postgresql check db setup section)
- cd src
- To run the rest api `./run` to run UI `python pyui/manage.py runserver 127.0.0.1:8000`
- Visit 127.0.0.1:8000 to use the app

Note:
1. if you are using postgresql or mysql with this project, make sure they are installe into the system.
2. To modify config settings vim src/pygmy/config/pygmy.cfg
3. You can run pygmy shell present in src directory to run the program on terminal


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

It uses JWT. When user logs in using username and password a token is generated that is amrked as fresh and it has a time period of 30 minutes. After 30 minutes. When a request comes with the old token and new token is generated from the refresh token api. This refreshed token has a new field `fresh=False`. This new token can only shorten the url and refresh the token for further user. It CAN'T reset the password, disable the link and change the secret key of the url.

DB Setup:
---------

**Use MySQL:**

`pip install pymysql`

Check correct port:

`mysqladmin variables | grep port`

Enter below line in src/pygmy/core/pygmy.cfg fro database->url value

`mysql+pymysql://root:root@127.0.0.1:3306/pygmy`

Enter mysql url

`CREATE DATABASE pygmy;`


**Use Postgresql**

`pip install psycopg2`

`postgres://amit@127.0.0.1:5432/pygmy`

Use Sqlite
==========

Sqlite is natively supported in Python

`sqlite:////var/lib/pygmy/pygmy.db`

Shell Usage
===========

Open shell using ./pygmy/src/shell. Availbale context are pygmy, Config, db, etc. See all context by using pygmy_context.

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

In [7]: # Create custom short url

In [8]: shorten('http://iamit.xyz', short_code='amit')
Out[8]:
{'long_url': 'http://iamit.xyz',
 'short_code': 'amit',
 'short_url': 'http://pygy.co/amit'}

In [9]: shorten?
Signature: shorten(long_url, short_code=None, expire_after=None, description=None, secret_key=None, owner=None, request=None)
Docstring:
    Helper class that has been delicated the task of inserting the
    passed url in DB, base 62 encoding from db id and return the short
    url value.
```

Link stats:
===========

For getting geo location stats from IP maxminds's GeoLite2-Country.mmd database is used. Its in src/pygmy/app folder.

License
=======

The MIT license (MIT)