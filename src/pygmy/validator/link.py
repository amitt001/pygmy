from marshmallow import Schema, fields, post_dump
from pygmy.utilities.urls import make_short_url
from pygmy.utilities.utils import make_url_from_id


class LinkSchema(Schema):
    id = fields.Method('create_id_link', dump_only=True)
    long_url = fields.URL(required=True)
    short_code = fields.Str(required=False, allow_none=True)
    short_url = fields.Method('short_url_path', load_only=True)
    description = fields.Str(required=False, allow_none=True)
    secret_key = fields.Str(required=False, allow_none=True)
    hits_counter = fields.Int(dump_only=True)
    expire_after = fields.Int(required=False, allow_none=True)
    is_protected = fields.Bool(default=False, required=False, allow_none=True)
    is_disabled = fields.Bool(default=False, required=False)
    is_custom = fields.Bool(default=False, required=False)
    owner = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime()

    # @pre_load
    # def process_short_url(self, data):
    #     custom_url = data.get('short_url')

    def short_url_path(self, link):
        if link and link.short_code:
            return make_short_url(link.short_code)

    def create_id_link(self, link):
        if link and link.id:
            return make_url_from_id(link.id, 'link')

    @post_dump
    def make_user_id(self, data):
        if data and data.get('owner'):
            data['owner'] = make_url_from_id(data['owner'], 'user')
        return data
                    # @pre_dump
    # def format_short_url(self, data):
    #     if link and link.short_code:
        # if isinstance(data, dict):
        #     data['short_url'] = make_short_url(data['short_url'])
        # return data
