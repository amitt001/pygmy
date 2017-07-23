from flask import request, redirect, abort, jsonify
from flask.views import MethodView
from pygmy.app.urlshortner import shorten, unshorten
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.model import LinkManager
from pygmy.validator import LinkSchema
from pygmy.utilities.urls import make_short_url, validate_url
from sqlalchemy.exc import IntegrityError


class LongUrlApi(MethodView):
    """View for handeling long url operations."""
    schema = LinkSchema()
    manager = LinkManager()

    def get(self):
        """Return data if long url already exists."""
        long_url = request.args.get('url')
        is_valid = validate_url(long_url)
        if is_valid is False:
            return jsonify(dict(error='Invalid URL.')), 400
        link = self.manager.get(long_url)
        if link is None:
            abort(404)
        result = self.schema.dump(link)
        return jsonify(result.data), 200

    def post(self):
        payload = request.get_json()
        data, errors = self.schema.load(payload)
        if errors:
            return jsonify(errors), 400
        long_url = data.pop('long_url')
        is_valid = validate_url(long_url)
        if is_valid is False:
            return jsonify(dict(error='Not a valid URL.')), 400
        try:
            link = self.manager.add(long_url, **data)
        except IntegrityError:
            return jsonify(dict(error='URL already exists.')), 400
        result = self.schema.dump(link)
        return jsonify(result.data), 201


class ShortURLApi(MethodView):
    """Short url view."""
    schema = LinkSchema()
    manager = LinkManager()

    def get(self):
        short_url = request.args.get('url')
        is_valid = validate_url(short_url)
        if is_valid is False:
            return jsonify(dict(error='Invalid URL.')), 400
        try:
            long_url = unshorten(short_url, api_call=True)
        except URLAuthFailed:
            abort(403)
        except URLNotFound:
            abort(404)
        result = self.schema.dump(long_url)
        return jsonify(result.data), 200

    def post(self):
        pass


def resolve(code):
    """Resolve the short url. code=301 PERMANENT REDIRECTION"""
    # TODO not needed
    short_url = make_short_url(code)
    try:
        long_url = unshorten(short_url, api_call=True, hit=True)
    except URLAuthFailed:
        abort(403)
    except URLNotFound:
        abort(404)
    return redirect(long_url.long_url, code=301)


def dummy():
    return '', 204
