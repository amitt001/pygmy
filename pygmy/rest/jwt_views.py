from flask import jsonify

from pygmy.rest.manage import jwt
from pygmy.app.auth import APITokenAuth, TokenAuth


@jwt.expired_token_loader
def expire_token_loader(jwt_header, jwt_payload):
    """Called in case an access token has expired. Reponse of this view is
    used to call the refresh token endpoint."""
    return jsonify(dict(
        status=401,
        sub_status=101,
        msg='The token has expired')), 401


@APITokenAuth.token_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_identity = APITokenAuth.get_jwt_identity()
    token = TokenAuth().create_access_token(identity=user_identity)
    return jsonify(dict(access_token=token)), 200
