from pygmy.config import config
from urllib.parse import urljoin, urlparse


def make_short_url(short_path):
    base_url = "{0}://{1}:{2}".format(
        config.schema, config.host, config.port)
    short_url = urljoin(base_url, short_path)
    return short_url


def get_short_path(short_url):
    parts = urlparse(short_url)
    short_path = parts.path.lstrip('/')
    return short_path
