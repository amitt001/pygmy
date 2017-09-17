from pygmy.utilities.urls import make_short_url, get_short_path
from pygmy.core.hashdigest import HashDigest
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.helpers.link_helper import next_short_code
from pygmy.model.link import LinkManager
from pygmy.exception.error import LinkExpired


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
        return make_short_url(urlobj.short_code)
    url_manager.add(long_url=long_url)
    short_path = next_short_code()
    url_manager.update(short_code=short_path)
    pygmy_link = make_short_url(short_path)
    return pygmy_link


def unshorten(short_url, secret_key=None, hit=False,
              query_by_code=False):
    """For performance benefit its better to calculate id out of short url and
    query long url from the db. Also increments hits counter.

    - To support custom url `query_by_code` flag query db with directly.

    :param short_url: The shortened url.
    :type short_url: string
    :param secret_key: secret key for url
    :param hit: increment hit counter
    :type hit: bool
    :param query_by_code: bool to query directly with short url string
    :type hit: bool
    :return: The full url
    :rtype: string"""
    url_manager = LinkManager()
    short_path = get_short_path(short_url)
    if query_by_code is True:
        query_dict = dict(short_code=short_path)
    else:
        # TODO: remove this
        _id = HashDigest().decode(short_path)
        query_dict = dict(id=_id)
    link = url_manager.find(**query_dict)
    if link is None:
        raise URLNotFound(short_url)
    if url_manager.has_expired():
        raise LinkExpired
    if link.is_protected:
        if not secret_key or link.secret_key != secret_key:
            raise URLAuthFailed(short_url)
    if hit:
        url_manager.click_counter()
    return link


def resolve_short(short_url, click_counter=False):
    """Returns the unshortened long url from short url
    :param short_url: str
    :param click_counter: bool
    :return: str
    """
    manager = LinkManager()
    link = manager.get_by_code(short_code=short_url)
    assert link is not None
    if manager.has_expired() is True:
        raise LinkExpired('Link has expired')
    if click_counter:
        link.click_counter()
    return link.long_url
