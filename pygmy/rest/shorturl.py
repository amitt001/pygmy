from flask import request, redirect, abort, jsonify
from flask.views import MethodView

from pygmy.app.auth import APITokenAuth
from pygmy.app.link import unshorten, resolve_short, link_stats
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.exception.error import LinkExpired, ShortURLUnavailable
from pygmy.model import LinkManager, UserManager
from pygmy.validator import LinkSchema, ValidationError
from pygmy.utilities.urls import validate_url
from pygmy.core.logger import log


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
            return jsonify(dict(error="Link has expired")), 404
        if link is None:
            abort(404)
        result = self.schema.dump(link)
        return jsonify(result), 200

    @APITokenAuth.token_required(optional=True)
    def post(self):
        payload = request.get_json()
        try:
            data = self.schema.load(payload)
        except ValidationError as errors:
            log.error('Error in the request payload %s', errors)
            err_msg = errors.messages_dict
            if err_msg.get('long_url'):
                err_msg.update({'error': err_msg.get('long_url')})
            return jsonify(err_msg), 400

        # if authenticated request check valid user
        user_email = APITokenAuth.get_jwt_identity()
        if user_email:
            user = UserManager().find(email=user_email)
            if not user:
                return jsonify(dict(error='Invalid user')), 400
            data['owner'] = user.id

        long_url = data.pop('long_url')
        log.info('Shortening url %s', long_url)
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
        log.info('Url: %s shortened, response: %s', long_url, result.get('short_code'))
        return jsonify(result), 201


class ShortURLApi(MethodView):
    """Short url view. The initial approach was to get `id` out of short url
    and query the db with primary key `id` but due to custom link the approach
    now is to simply query the db with short url code.
    Check how to improve this."""
    schema = LinkSchema()

    def get(self):
        secret = request.headers.get('secret_key')
        short_url = request.args.get('url')
        try:
            long_url = unshorten(short_url, secret_key=secret,
                                 query_by_code=True, request=request)
            result = self.schema.dump(long_url)
        except LinkExpired:
            return jsonify(dict(error="Link has expired")), 410
        except URLAuthFailed:
            return jsonify(dict(error="Secret key not provided")), 403
        except URLNotFound:
            return jsonify(
                dict(error="URL Not Found Or Expired")), 404
        return jsonify(result), 200


@APITokenAuth.token_required(optional=True)
def resolve(code):
    """Resolve the short url. code=301 PERMANENT REDIRECTION"""
    secret_key = request.headers.get('secret_key')
    try:
        # check if link is not a secret link
        if code.startswith('+') or code.endswith('+'):
            stats = link_stats(code)
            response = jsonify(stats)
            if stats is None:
                response = jsonify({'error': 'URL not found or disabled'}), 404
        else:
            long_url = resolve_short(
                code.strip('+'), request=request, secret_key=secret_key)
            response = redirect(long_url, code=301)
    except LinkExpired:
        response = jsonify(dict(error="Link has expired")), 404
    except URLAuthFailed:
        response = jsonify({'error': 'Access to URL forbidden'}), 403
    except (URLNotFound, AssertionError):
        response = jsonify({'error': 'URL not found or disabled'}), 404
    return response


def dummy():
    return '', 204
