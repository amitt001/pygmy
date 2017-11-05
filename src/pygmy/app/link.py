from pygmy.config import config
from pygmy.core.hashdigest import HashDigest
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.exception.error import LinkExpired
from pygmy.helpers.link_helper import next_short_code
from pygmy.model.link import LinkManager
from pygmy.model.clickmeta import ClickMetaManager
from pygmy.utilities.urls import make_short_url, get_short_path


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


def unshorten(short_url, secret_key=None,
              query_by_code=False, request=None):
    """For performance benefit its better to calculate id out of short url and
    query long url from the db. Also increments hits counter.

    - To support custom url `query_by_code` flag query db with directly.

    :param short_url: The shortened url.
    :type short_url: string
    :param secret_key: secret key for url
    :param query_by_code: bool to query directly with short url string
    :param request: http request object. When request is not None parse the
        request object and get stats out of it.
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
    if request:
        save_clickmeta(request, link)
    return link


def resolve_short(short_code, request=None):
    """Returns the unshortened long url from short url

    :param short_code: str
    :param request: http request object. When request is not None parse the
        request object and get stats out of it.
    :return: str
    """
    manager = LinkManager()
    link = manager.get_by_code(short_code=short_code)
    assert link is not None
    if manager.has_expired() is True:
        raise LinkExpired('Link has expired')
    # put stats
    if request:
        save_clickmeta(request, link)
    return link.long_url


def link_stats(short_code):
    """Get short link stats"""
    manager = LinkManager()
    short_code = short_code.strip('+')
    link = manager.get_by_code(short_code=short_code)
    if link is None:
        return None
    formatted_stats = formatted_link_stats(link)
    return formatted_stats


def formatted_link_stats(link):
    """Pass link and clickmeta model objects ans returns a formatted dict.

    :param link:
    :param clickmeta:
    :return:
    """
    manager = ClickMetaManager()
    click_meta = manager.click_stats(link.id)
    link_info = dict(
            long_url=link.long_url,
            short_code=link.short_code,
            created_at=link.created_at
    )
    """
    If month:
        30 Days
    If hour:
        24 hours
    if minutes:
        60 minutes
    """
    click_info = {
        'total_hits': click_meta.get('hits', 0),
        'country_stats': click_meta.get('country_hits', 0),
        'referrer': click_meta.get('referrer_hits', 0),
        'time_series_base': click_meta.get('time_base'),
        'time_stats': click_meta.get('timestamp_hits', 0),
    }
    return {**link_info, **click_info}


def save_clickmeta(request, link):
    """Save public access info of short link.

    :param request:
    :param link:
    :return: ClickMeta
    """
    from pygmy.core.request_parser import parse_request, parse_header
    pygmy_header_key = config.pygmy_internal['pygmy_header_key']
    if request.headers.get('Pygmy-Header-Key') == pygmy_header_key:
        data = parse_header(request)
    else:
        data = parse_request(request)
    return ClickMetaManager().add(link_id=link.id, **data)
