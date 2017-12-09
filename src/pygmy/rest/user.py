from flask import request, jsonify
from flask.views import MethodView
from passlib.hash import bcrypt

from pygmy.model import UserManager, LinkManager
from pygmy.validator.user import UserSchema
from pygmy.validator.link import LinkSchema
from pygmy.app.auth import APITokenAuth, TokenAuth


class UserApi(MethodView):
    """Signup and get user info"""
    schema = UserSchema()

    def get(self, user_id=None):
        params = dict()
        if user_id is not None:
            user = UserManager().get(user_id)
        elif request.args.get('email'):
            params['email'] = request.args.get('email')
            user = UserManager().find(**params)
        if user is None:
            return jsonify(dict(error="User not found")), 404
        result = self.schema.dump(user)
        return jsonify(result.data), 200

    def post(self):
        # TODO: post should behave like upsert
        manager = UserManager()
        payload = request.get_json()
        data, errors = self.schema.load(payload)
        if errors:
            return jsonify(errors), 400
        if manager.find(email=data['email']):
            return jsonify(dict(error='User exists')), 400
        user = manager.add(**data)
        result = self.schema.dump(user).data
        tokens = TokenAuth().create_token(
            identity=payload.get('email'))
        result.update(tokens)
        return jsonify(result), 201


class Auth(MethodView):
    """User login class."""
    schema = UserSchema()

    def post(self):
        params = request.get_json()
        email = params.get('email')
        password = params.get('password')
        if not email:
            return jsonify(dict(error="Missing email required.")), 400
        if not password:
            return jsonify(dict(error="Missing password required.")), 400

        user = UserManager().find(email=email)
        if user is None:
            return jsonify(dict(
                error='No user found with email: {}'.format(email))), 404
        if email != user.email or not bcrypt.verify(password, user.password):
            return jsonify(dict(error="Invalid username or password.")), 400
        result = self.schema.dump(user).data
        tokens = TokenAuth().create_token(identity=email)
        result.update(tokens)
        return jsonify(result), 200


@APITokenAuth.token_required
def get_links(user_id=None):
    """Get all links that belong to user `user_id`"""
    # TODO: get auth required from settings and get user links by id

    manager = LinkManager()
    schema = LinkSchema()
    if request.method == 'GET':
        user_email = APITokenAuth.get_jwt_identity()
        if not user_email:
            return jsonify(dict(error='Invalid/expired token passed')), 400
        user = UserManager().get_by_email(email=user_email)
        if not user:
            return jsonify(dict(error='Invalid/expired token passed')), 400
        links = manager.get_by_owner(owner_id=user.id)
        if not links:
            return jsonify([]), 200
        result = schema.dump(links, many=True)
        return jsonify(result.data)
