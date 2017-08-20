"""User model serializer/validator"""
from marshmallow import Schema, fields
from pygmy.utilities.utils import make_url_from_id


class UserSchema(Schema):
    id = fields.Method('create_id_link', dump_only=True)
    email = fields.Email(required=True)
    f_name = fields.Str(required=True)
    m_name = fields.Str(required=False, default='', allow_none=True)
    l_name = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    link = fields.Method('links_link', load_only=True)

    def create_id_link(self, user):
        if user and user.id:
            return make_url_from_id(user.id, 'user')

    def links_link(self, user):
        if user and user.id:
            return make_url_from_id(user.id, 'links_list')
