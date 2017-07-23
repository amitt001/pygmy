from pygmy.utilities.urls import make_short_url, get_short_path
from pygmy.core.hashdigest import HashDigest
from pygmy.exception import URLNotFound, URLAuthFailed
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

    url_manager = LinkManager()
    urlobj = url_manager.find(long_url=long_url)
    if urlobj is not None:
        return make_short_url(urlobj.short_url)
    url_manager.add(long_url=long_url)
    short_path = HashDigest().shorten(url_manager.link.id)
    url_manager.update(short_url=short_path)
    pygmy_link = make_short_url(short_path)
    return pygmy_link


def unshorten(short_url, secret=None, api_call=False, hit=False):
    """For performance benefit its better to calculate id out of short
    url and query long url from the db. Also increments hits counter.

    :param short_url: The shortened url.
    :type short_url: string
    :param secret: secret key for url
    :type api_call: string
    :param api_call: is an api call?
    :type api_call: bool
    :return: The full url.
    :rtype: string"""

    # TODO: increment counter when called from rest.
    short_path = get_short_path(short_url)
    _id = HashDigest().decode(short_path)
    url_manager = LinkManager()
    link = url_manager.find(id=_id)
    if link is None:
        raise URLNotFound(short_url)
    if link.is_protected:
        if not secret or link.secret != secret:
            raise URLAuthFailed(short_url)
    if hit:
        url_manager.click_counter()
    if api_call:
        return link
    return link.long_url
