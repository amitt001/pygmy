from pygmy.rest.shorturl import url_unshorten, url_shorten, resolve
from pygmy.rest.manage import app



app.add_url_rule(
    '/tiny', view_func=url_shorten, methods=['GET'])
app.add_url_rule(
    '/full', view_func=url_unshorten, methods=['GET'])
app.add_url_rule(
    '/<code>', view_func=resolve, methods=['GET'])
