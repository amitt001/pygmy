from pygmy.rest.shorturl import (
    LongUrlApi, ShortURLApi, resolve, dummy, link_stats)
from pygmy.rest.user import UserApi, Auth, get_links
from pygmy.rest.jwt_views import refresh
from pygmy.rest.manage import app

ONLY_GET = ['GET']
GET_POST = ['GET', 'POST']
ONLY_POST = ['POST']

app.add_url_rule(
    '/api/shorten', view_func=LongUrlApi.as_view('long_url'), methods=GET_POST)
app.add_url_rule(
    '/api/unshorten', view_func=ShortURLApi.as_view('short_url'),
    methods=GET_POST)

# user APIs
app.add_url_rule(
    '/api/user', view_func=UserApi.as_view('user_create'),
    methods=ONLY_POST)
app.add_url_rule(
    '/api/user/<user_id>', view_func=UserApi.as_view('user_view'),
    methods=GET_POST)
app.add_url_rule(
    '/api/user/<user_id>/links', view_func=get_links,
    methods=GET_POST)
app.add_url_rule(
    '/api/user/links', view_func=get_links,
    methods=GET_POST)

# Token auth
app.add_url_rule('/api/login', view_func=Auth.as_view('user_login'),
                 methods=GET_POST)

app.add_url_rule('/token/refresh', view_func=refresh, methods=ONLY_POST)
# app.add_url_rule('/api/token/', user_view.get_token, name='token'),
# app.add_url_rule(r'verify/?$', verify_jwt_token, name='verify'),

# General
app.add_url_rule('/favicon.ico', view_func=dummy, methods=ONLY_GET)

# This should be last
app.add_url_rule('/<code>', view_func=resolve, methods=ONLY_GET)
