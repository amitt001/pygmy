from flask import request, redirect, abort, jsonify
from flask.views import MethodView

from pygmy.app.auth import APITokenAuth
from pygmy.app.link import unshorten, resolve_short, link_stats
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.exception.error import LinkExpired, ShortURLUnavailable
from pygmy.model import LinkManager, UserManager
from pygmy.validator import LinkSchema
from pygmy.utilities.urls import validate_url


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

    @APITokenAuth.token_optional
    def post(self):
        payload = request.get_json()
        data, errors = self.schema.load(payload)
        # if authenticated request check valid user
        user_email = APITokenAuth.get_jwt_identity()
        if user_email:
            user = UserManager().find(email=user_email)
            if not user:
                return jsonify(dict(error='Invalid user')), 400
            data['owner'] = user.id
        if errors:
            return jsonify(errors), 400
        long_url = data.pop('long_url')
        link = self.manager.get(long_url)
        if link is None or (
                        data.get('is_custom') or
                        data.get('is_protected') or
                        data.get('expire_after')):
            try:
                link = self.manager.add(long_url, **data)
            except ShortURLUnavailable as e:
                return jsonify(dict(error=str(e))), 400
        result = self.schema.dump(link)
        return jsonify(result.data), 201


class ShortURLApi(MethodView):
    """Short url view. The initial approach was to get `id` out of short url
    and query the db with primary key `id` but due to custom link the approach
    now is to simply query the db with short url code.
    Check how to improve this."""
    schema = LinkSchema()

    def get(self):
        secret = request.headers.get('secret_key')
        short_url = request.args.get('url')
        is_valid = validate_url(short_url)
        if is_valid is False:
            return jsonify(dict(error='Invalid URL.')), 400
        try:
            long_url = unshorten(short_url, secret_key=secret,
                                 query_by_code=True, request=request)
            result = self.schema.dump(long_url)
        except LinkExpired:
            return jsonify(dict(message="Link has expired")), 410
        except URLAuthFailed:
            return jsonify(dict(message="Secret key not provided")), 403
        except URLNotFound:
            return jsonify(dict(message="Invalid/Expired url")), 404
        return jsonify(result.data), 200


@APITokenAuth.token_optional
def resolve(code):
    """Resolve the short url. code=301 PERMANENT REDIRECTION"""
    # TODO not needed
    user_email = APITokenAuth.get_jwt_identity()
    secret_key = request.headers.get('secret_key')
    try:
        # check if link is not a secret link
        long_url = resolve_short(
            code.strip('+'), request=request, secret_key=secret_key)
        if code.startswith('+') or code.endswith('+'):
            stats = link_stats(code)
            response = jsonify(stats)
            if stats is None:
                response = jsonify({'error': 'URL not found or disabled'}), 404
        else:
            response = redirect(long_url, code=301)
    except LinkExpired:
        response = jsonify(dict(message="Link has expired")), 404
    except URLAuthFailed:
        response = jsonify({'error': 'Access to URL forbidden'}), 403
    except URLNotFound:
        response = jsonify({'error': 'URL not found or disabled'}), 404
    return response


def dummy():
    return '', 204
