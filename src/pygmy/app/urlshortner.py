from urllib.parse import urljoin, urlparse

from pygmy.config import config
from pygmy.core.hashdigest import HashDigest
from pygmy.exception.invalidurl import URLNotFound
from pygmy.model.url import URLManager


def make_short_url(short_path):
    base_url = "{0}://{1}:{2}".format(
        config.schema, config.host, config.port)
    short_url = urljoin(base_url, short_path)
    return short_url


def get_short_path(short_url):
    parts = urlparse(short_url)
    short_path = parts.path.lstrip('/')
    return short_path


def shorten(full_url):
    """Helper class that has been delicated the task of inserting the
    passed url in DB, base 62 encoding from db id and return the short
    url value.

    :param full_url: Fully qualified url
    :type full_url: string
    :return: The short url.
    :rtype: string
    """

    hashdigest = HashDigest()
    url_manager = URLManager()
    urlobj = url_manager.find(full_url=full_url)
    if urlobj is not None:
        return urlobj.short_url
    url_manager.add(full_url=full_url)
    short_path = hashdigest.shorten(url_manager.url.id)
    url_manager.update(short_url=short_path)
    pygmy_link = make_short_url(short_path)
    return pygmy_link


def unshorten(short_url):
    """For performance benefit its better to calculate id out of short url
    and query the full url from db. Also increments hits counter.

    :param short_url: The shortened url.
    :type short_url: string
    :return: The full url.
    :rtype: string"""

    # TODO: increment counter when called from rest.
    short_path = get_short_path(short_url)
    hashdigest = HashDigest()
    _id = hashdigest.decode(short_path)
    url_manager = URLManager()
    url = url_manager.find(id=_id)
    if url is None:
        raise URLNotFound(short_url)
    return url.full_url


def dummy():
    url_manager = None
    url_manager.incr_counter()
    url_manager.decr_counter()





