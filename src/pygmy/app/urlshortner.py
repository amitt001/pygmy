from pygmy.utilities.urls import make_short_url, get_short_path
from pygmy.core.hashdigest import HashDigest
from pygmy.exception.invalidurl import URLNotFound
from pygmy.model.link import LinkManager


def shorten(long_url):
    """Helper class that has been delicated the task of inserting the
    passed url in DB, base 62 encoding from db id and return the short
    url value.

    :param long_url: Fully qualified url
    :type long_url: string
    :return: The short url.
    :rtype: string
    """

    hashdigest = HashDigest()
    url_manager = LinkManager()
    urlobj = url_manager.find(long_url=long_url)
    if urlobj is not None:
        return make_short_url(urlobj.short_url)
    url_manager.add(long_url=long_url)
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
    url_manager = LinkManager()
    link = url_manager.find(id=_id)
    if link is None:
        raise URLNotFound(short_url)
    return link.long_url


def dummy():
    url_manager = None
    url_manager.incr_counter()
    url_manager.decr_counter()





