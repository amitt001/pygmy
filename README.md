<p align="center"><img src="pygmyui/static/logo/logov2.png" alt="pygmy" height="200px"></p>

# Pygmy

[![Build Status](https://travis-ci.org/amitt001/pygmy.svg?branch=master)](https://travis-ci.org/amitt001/pygmy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/amit19)

Live version of this project @ [https://pygy.co](https://pygy.co)

Check link stats by adding **+** to the URL. Example [pygy.co/pygmy+](https://pygy.co/pygmy+)

*Note that pygy.co is a demo website for this project and should be used as such. While the website is going to be up for the foreseeable future, its future depends on the sponsorship and hosting that I get. Currently, project is hosted on Digitalocean, as they were kind enough to offer me one year of sponsorship. I would like to keep the project website up and maintain the project but I do not make any money out of this project or website.
If you would like to supprt the project, I can be contacted on my email of sources listed on websites contact page.*

# Table of Contents
- [Pygmy](#pygmy)
- [Table of Contents](#table-of-contents)
    - [Features](#features)
    - [Technical Info](#technical-info)
    - [Installation/Setup](#installationsetup)
        - [Docker](#docker)
        - [Manual(from source)](#manualfrom-source)
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
    - [Donations](#donations)
    - [Sponsorship](#sponsorship)
    - [License](#license)

Pygmy or `pygy.co` is an open-source, extensible & easy-to-use but powerful URL shortener. It's created keeping in mind that it should be easy to host and run your custom URL shortener without much effort. [Open-source Python URL shortener]

The architecture is very loosely coupled which allows custom integrations easily.

**The project has 3 major parts**

- The core URL shortening code
- A REST API on top. Uses Flask framework
- The UI layer for rendering the UI. It uses Django framework

## Features

- URL shortner
- Customized short URL's(ex: `pygy.co/pygmy`)
- Support to create auto expiry URL after sometime.
- Secret key protected URL's
- User Login/Sign up to track shortned URL's and link stats
- User dashboard
- Link Analytics(add + to the tiny URL to get link stats)

## Technical Info

- Python 3, Javascript, JQuery, HTML, CSS
- REST API: Flask
- Pygmyui: Django(It serves the web user interface)
- DB: PostgreSQL/MySQL/SQLite
- Others: SQLAlchmey, JWT
- Docker

## Installation/Setup

### Docker

1. In terminal run this command: `docker pull amit19/pygmy`
2. Then run the container: `docker run -it -p 8000:8000 amit19/pygmy`
3. Open http://localhost:8000 in your browser

### Manual(from source)

1. Clone `git clone https://github.com/amitt001/pygmy.git & cd pygmy`
2. (Optional) Install virtualenv (optional but recommended)
    - `virtualenv -p python3 env`
    - `source env/bin/activate`
3. Install dependencies: `pip3 install -r requirements.txt` (if you are using MySQL or PostgreSQL check [DB setup](#db-setup) section)
4. `python run.py` (It runs Flask and Django servers using gunicorn)
5. Visit `127.0.0.1:8000` to use the app
6. Logs can be viewed at `pygmy/data/pygmy.log`

Note:

 - **This module only supports Python 3. Make sure pip and virtualenv are both python 3 based versions.**(To install Python 3 on Mac: http://docs.python-guide.org/en/latest/starting/install3/osx/)
 - The project has two config files:
    - pygmy.cfg: `pygmy/config/pygmy.cfg` rest API and pygmy core settings file
    - settings.py: `pygmyui/pygmyui/settings.py` Django settings file
 - Both the files have aparallel <name>_test.<ext> config files to configure it for tests.
 - SQLite is default db, if you are using PostgreSQL or MySQL with this project, make sure they are installed into the system.
 - To modify config settings vim `pygmy/config/pygmy.cfg`
 - You can run pygmy shell present in src directory to run the program on terminal. `python shell`
 - By default in `pygmyui/pygmyui/settings.py` DEBUG is set to True, set it to False in production

## DB Setup:

### Use MySQL

First install `pymysql`:

`pip install pymysql`

Check correct port:

`mysqladmin variables | grep port`

Change below line in `pygmy/core/pygmy.cfg`:

```
engine: mysql
url: mysql+pymysql://root:root@127.0.0.1:3306/pygmy
```

Enter MySQL URL

`CREATE DATABASE pygmy;`

Note: Better using Mysql with version > `5.6.5` to use default value of `CURRENT_TIMESTAMP` for `DATETIME`.

### Use Postgresql

`pip install psycopg2`

`postgres://amit@127.0.0.1:5432/pygmy`

### Use SQLite

SQLite is natively supported in Python

`sqlite:////var/lib/pygmy/pygmy.db`

## Using Pygmy API

## Create User:
------------

    curl -XPOST http://127.0.0.1:9119/api/user/1 -H 'Content-Type: application/json' -d '{
    "email": "amit@gmail.com",
    "f_name": "Amit",
    "l_name": "Tripathi",
    "password": "a_safe_one"
    }'


*To be updated soon*

Get User:

Get All User Link:

Create Link:

Get Link:

## Shell Usage

Open shell using ./shell. Available context is pygmy, Config, DB, etc. See all context by using pygmy_context.

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

###### How Link Stats Are Generated?

For getting geo location stats from IP maxminds' [GeoLite2-Country.mmd](http://pygy.co/cm) database is used. It's in `pygmy/app` directory.

###### How Pygmy Auth Token Works?

It uses JWT. When user logs in using username and password two tokens are generated, refresh token and auth token. Auth token is used for authentication with the Pygmy API. Refresh token can only be used to generate new auth token. Auth token has a very short TTL but refresh token has a longer TTL. After 30 minutes. When a request comes with the old auht token and a new token is generated from the refresh token API. User passwords are encrypted by [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) hash algorithm.

## Development

If you find any bug, have a question or a general feature request. Open an issue on the 'Issue' page.

To contribute to project:

1. Clone the repo and make changes
2. Build the code: `docker build pygmy`
3. Test the chnages by running: `docker run -it -p 8000:8000 pygmy`
4. The website will be available at: http://127.0.0.1:8000/

Run tests and generate a coverage report:

`coverage run --source pygmy -m py.test`

See coverage report(Coverage is bad because the coverage for integration tests is not generated yet):

`coverage report`

## Contributions

Thanks [batarian71](https://github.com/batarian71) for providing the logo icon.

## Donations
If this project help you reduce time to develop, you can buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/amit19)

## Sponsorship

I would like to thank DigitalOcean for providing initial hosting to Pygmy project. Pygy.co is hosted on DigitalOcean.

<a href="https://www.digitalocean.com/"><img src="https://i.imgur.com/6cYodyH.png"></a>

## License

MIT License

Copyright (c) 2017 Amit Tripathi(https://twitter.com/amitt019)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[Read License Terms](https://github.com/amitt001/pygmy/blob/master/LICENSE)
