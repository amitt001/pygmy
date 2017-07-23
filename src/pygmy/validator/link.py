from marshmallow import Schema, fields
from pygmy.utilities.urls import make_short_url


class LinkSchema(Schema):
    id = fields.Int(dump_only=True)
    long_url = fields.Str(required=True)
    short_url = fields.Method('format_short_url', dump_only=True)
    description = fields.Str()
    hits_counter = fields.Int(dump_only=True)
    is_protected = fields.Bool(default=False)
    is_disabled = fields.Bool(default=False)
    owner = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime()

    def format_short_url(self, link):
        if link and link.short_url:
            return make_short_url(link.short_url)
