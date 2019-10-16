<p align="center"><img src="pygmyui/static/logo/logov2.png" alt="pygmy" height="200px"></p>

# Pygmy

[![Build Status](https://travis-ci.org/amitt001/pygmy.svg?branch=master)](https://travis-ci.org/amitt001/pygmy)
[![Coverage Status](https://img.shields.io/coveralls/github/amitt001/pygmy.svg?color=yellowgreen)](https://coveralls.io/github/amitt001/pygmy?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://github.com/amitt001/pygmy/blob/master/LICENSE)
![Docker Pulls](https://img.shields.io/docker/pulls/amit19/pygmy.svg)
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/amit19)

Live version of this project @ [https://pygy.co](https://pygy.co)

Check link stats by adding **+** to the URL. Example [pygy.co/pygmy+](https://pygy.co/pygmy+)

Hackernews Thread: [https://news.ycombinator.com/item?id=17690559](https://pygy.co/pygmyHN)

*Note that pygy.co is a demo website for this project and should be used as such. While the website is going to be up for the foreseeable future, its future depends on the sponsorship and hosting that I get. Currently, the project is hosted on Digitalocean, as they were kind enough to offer me one year of sponsorship. I would like to keep the project website up and maintain the project but I do not make any financial gains out of this project or website. Website is
free to use and is completely ad-free.
If you would like to support the project, Please use the donate link in [Donations](#donations) section.*

# Table of Contents
- [Pygmy](#Pygmy)
- [Table of Contents](#Table-of-Contents)
  - [Features](#Features)
  - [Technical Info](#Technical-Info)
  - [Installation/Setup](#InstallationSetup)
    - [Docker](#Docker)
    - [Manual(from source)](#Manualfrom-source)
  - [DB Setup:](#DB-Setup)
    - [Use MySQL](#Use-MySQL)
    - [Use Postgresql](#Use-Postgresql)
    - [Use SQLite](#Use-SQLite)
  - [Docker](#Docker-1)
  - [Using Pygmy API](#Using-Pygmy-API)
    - [Create User:](#Create-User)
  - [Shell Usage](#Shell-Usage)
          - [How Link Stats Are Generated?](#How-Link-Stats-Are-Generated)
          - [How Pygmy Auth Token Works?](#How-Pygmy-Auth-Token-Works)
  - [Development](#Development)
  - [Contributions](#Contributions)
  - [Donations](#Donations)
  - [Sponsorship](#Sponsorship)
  - [License](#License)

Pygmy or `pygy.co` is an open-source, extensible & easy-to-use but powerful URL shortener. It's created keeping in mind that it should be easy to host and run your custom URL shortener without much effort. [Open-source Python URL shortener]

The architecture is very loosely coupled which allows custom integrations easily.

**The project has 3 major parts**

- The core URL shortening code
- A REST API on top. Uses Flask framework
- The UI layer for rendering the UI. It uses the Django framework

## Features

- URL shortener
- Customized short URL's(ex: `pygy.co/pygmy`)
- Support to create auto expiry URL after some time.
- Secret key protected URL's
- User Login/Sign up to track shortened URL's and link stats
- User dashboard
- Link Analytics(add + to the tiny URL to get link stats)

## Technical Info

- Python 3, Javascript, JQuery, HTML, CSS
- REST API: Flask
- Pygmyui: Django(It serves the web user interface)
- DB: PostgreSQL/MySQL/SQLite
- Others: SQLAlchmey, JWT
- Docker
- Docker-compose

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
 - SQLite is default DB, if you are using PostgreSQL or MySQL with this project, make sure they are installed into the system.
 - You can run pygmy shell also. Present in the root directory. To run the program on the terminal: `python shell`
 - By default, DEBUG is set to True in `pygmyui/pygmyui/settings.py` file, set it to False in production.

## DB Setup:

By default, Pygmy uses SQLite but any of the DB, SQLite, MySQL or PostgreSQL, can be used. Configs is present at `pygmy/config/pygmy.cfg`.

Use DB specific instruction below. Make sure to check and modify values in pygmy.cfg file according to your DB setup.

### Use MySQL

First, install `pymysql`:

`pip install pymysql`

Check correct port:

`mysqladmin variables | grep port`

Change below line in `pygmy/core/pygmy.cfg`:

```
[database]
engine: mysql
url: {engine}://{user}:{password}@{host}:{port}/{db_name}
user: root
password: root
host: 127.0.0.1
port: 3306
db_name: pygmy
```

Enter MySQL URL

`CREATE DATABASE pygmy;`

Note: It's better to use Mysql with version > `5.6.5` to use the default value of `CURRENT_TIMESTAMP` for `DATETIME`.

### Use Postgresql

Change below line in `pygmy/core/pygmy.cfg`:

```
[database]
engine: postgresql
url: {engine}://{user}:{password}@{host}:{port}/{db_name}
user: root
password: root
host: 127.0.0.1
port: 5432
db_name: pygmy
```

### Use SQLite

SQLite is natively supported in Python

`sqlite:////var/lib/pygmy/pygmy.db`

```
[database]
engine: sqlite3
sqlite_data_dir: data
sqlite_db_file_name: pygmy.db
```

## Docker

Docker image name: amit19/pygmy

Docker image can be built by: `docker build -t amit19/pygmy .`

Both the Dockerfile and docker-compose file are present at the root of the project.

To use docker-compose you need to pass DB credentials in the docker-compose file

## Using Pygmy API

### Create User:

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

In [5]: # check the available context of the shell
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

It uses JWT. When user logs in using username and password two tokens are generated, refresh token and auth token. Auth token is used for authentication with the Pygmy API. The refresh token can only be used to generate a new auth token. Auth token has a very short TTL but refresh token has a longer TTL. After 30 minutes. When a request comes with the old auth token and a new token is generated from the refresh token API. User passwords are encrypted by [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) hash algorithm.

## Development

If you find any bug, have a question or a general feature request. Open an issue on the 'Issue' page.

To contribute to the project:

1. Clone the repo and make changes
2. Build the code: `docker build pygmy`
3. Test the changer by running: `docker run -it -p 8000:8000 pygmy`
4. The website will be available at http://127.0.0.1:8000/

Run tests:

In root directory run this command: `py.test`

Or with coverage report(`pip install coverage`):

`coverage run --omit="*/templates*,*/venv*,*/tests*" -m py.test`

See coverage report(Coverage is bad because the coverage for integration tests is not generated yet):

`coverage report`

## Contributions

Thanks [batarian71](https://github.com/batarian71) for providing the logo icon.

## Donations

I do not run any ads on this project. The server(currently paid by DigitalOcean till Jan 2019) or domain cost, I pay out of my pocket. However, this can't continue forever.

If you find this project helpful, you can help me keep this project running in future by donating any amount you see fit :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/amit19)

## Sponsorship

I would like to thank DigitalOcean for providing initial hosting to the Pygmy project. Pygy.co is hosted on DigitalOcean.

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
