from flask import request, redirect, abort, jsonify
from flask.views import MethodView

from pygmy.app.urlshortner import unshorten
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.model import LinkManager
from pygmy.validator import LinkSchema
from pygmy.utilities.urls import make_short_url, validate_url


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
        if self.manager.has_expired():
            return jsonify(dict(message="Link has expired")), 404
        if link is None:
            abort(404)
        result = self.schema.dump(link)
        return jsonify(result.data), 200

    def post(self):
        payload = request.get_json()
        data, errors = self.schema.load(payload)
        print(data)
        if errors:
            return jsonify(errors), 400
        long_url = data.pop('long_url')
        is_valid = validate_url(long_url)
        if is_valid is False:
            return jsonify(dict(error='Not a valid URL.')), 400
        link = self.manager.get(long_url)
        if link is None or (
                        data.get('is_custom') or
                        data.get('is_protected') or
                        data.get('expire_after')):
            link = self.manager.add(long_url, **data)
        result = self.schema.dump(link)
        return jsonify(result.data), 201


class ShortURLApi(MethodView):
    """Short url view. The initial approach was to get `id` out of short url
    and query the db with primary key `id` but due to custom link the approach
    now is to simply query the db with short url code.
    Check how to improve this."""
    schema = LinkSchema()

    def get(self):
        short_url = request.args.get('url')
        secret = request.headers.get('secret_key')
        is_valid = validate_url(short_url)
        if is_valid is False:
            return jsonify(dict(error='Invalid URL.')), 400
        try:
            long_url = unshorten(short_url, secret_key=secret,
                                 api_call=True, query_by_code=True)
            if LinkManager(long_url).has_expired():
                return jsonify(dict(message="Link has expired")), 404
        except URLAuthFailed:
            return jsonify(dict(message="Secret key not provided")), 403
        except URLNotFound:
            return jsonify(dict(message="Invalid/Expired url")), 404
        result = self.schema.dump(long_url)
        return jsonify(result.data), 200

    def post(self):
        pass


def resolve(code):
    """Resolve the short url. code=301 PERMANENT REDIRECTION"""
    # TODO not needed
    short_url = make_short_url(code)
    try:
        long_url = unshorten(short_url, api_call=True,
                             hit=True, query_by_code=True)
        if LinkManager(long_url).has_expired():
            return jsonify(dict(message="Link has expired")), 404
    except URLAuthFailed:
        return jsonify({'error': 'Access to URL forbidden'}), 404
    except URLNotFound:
        return jsonify({'error': 'URL not found or disabled'}), 404
    return redirect(long_url.long_url, code=301)


def dummy():
    return '', 204
