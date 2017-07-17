__all__ = ['url_shorten', 'url_unshorten']

from flask import request, redirect
from pygmy.app.urlshortner import shorten, unshorten
from pygmy.utilities.urls import make_short_url


def url_shorten():
    long_url = request.args.get('url')
    if not long_url:
        return "LOL"
    short_url = shorten(long_url)
    return short_url


def url_unshorten():
    short_url = request.args.get('url')
    if not short_url:
        return "LOL"
    long_url = unshorten(short_url)
    return long_url


def resolve(code):
    print(code)
    if code is None:
        return "LOL"
    # TODO not needed
    short_url = make_short_url(code)
    long_url = unshorten(short_url)
    return redirect(long_url, code=301)
