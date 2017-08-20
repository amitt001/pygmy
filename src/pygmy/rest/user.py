from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token, jwt_required
from passlib.hash import bcrypt
from pygmy.model import UserManager, LinkManager
from pygmy.validator.user import UserSchema
from pygmy.validator.link import LinkSchema


class UserApi(MethodView):
    schema = UserSchema()

    def get(self, user_id=None):
        params = dict()
        if user_id is not None:
            user = UserManager().get(user_id)
        elif request.args.get('email'):
            params['email'] = request.args.get('email')
            user = UserManager().find(**params)
        if user is None:
            return jsonify(dict(message="User not found")), 404
        result = self.schema.dump(user)
        return jsonify(result.data), 200

    def post(self, user_id=None):
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
        result['access_token'] = create_access_token(
            identity=payload.get('email'))
        return jsonify(result), 201


class Auth(MethodView):
    """User signup/login class."""
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
                error='User not found with email: {}'.format(email))), 404
        if email != user.email or not bcrypt.verify(password, user.password):
            return jsonify(dict(error="Invalid username or password.")), 400
        result = self.schema.dump(user).data
        result['access_token'] = create_access_token(identity=email)
        return jsonify(result), 200


# @jwt_required
def get_links(user_id):
    """Get all links that belong to user `user_id`"""
    manager = LinkManager()
    schema = LinkSchema()
    if request.method == 'GET':
        order_by = request.args.get('sort')
        links = manager.get_by_onwer(owner=user_id, order_by=order_by)
        if not links:
            return jsonify([])
        result = schema.dump(links, many=True)
        return jsonify(result.data)
