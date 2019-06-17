from pygmy.config import config
from pygmy.core.hashdigest import HashDigest
from pygmy.exception import URLNotFound, URLAuthFailed
from pygmy.exception.error import LinkExpired
from pygmy.helpers.link_helper import next_short_code
from pygmy.model.link import LinkManager
from pygmy.model.clickmeta import ClickMetaManager
from pygmy.utilities.urls import make_short_url, get_short_path
from pygmy.validator.link import LinkSchema


def shorten(long_url, short_code=None, expire_after=None, description=None,
            secret_key=None, owner=None, request=None):
    """Helper class that has been deligated the task of inserting the
    passed url in DB, base 62 encoding from db id and return the short
    url value.

    :param long_url:
    :param short_code:
    :param description:
    :param expire_after:
    :param secret_key:
    :param owner:
    :return:
    """
    url_manager = LinkManager()
    query_dict = dict(long_url=long_url, is_custom=False, is_protected=False)
    insert_dict = query_dict
    if short_code:
        query_dict.update(dict(short_code=short_code, is_custom=True))
        insert_dict = query_dict
    if secret_key:
        query_dict.update(secret_key=str(secret_key), is_protected=True)
        insert_dict = query_dict
    if expire_after:
        insert_dict['expire_after'] = expire_after
    urlobj = url_manager.find(**query_dict)
    if urlobj is None:
        url_manager.add(**insert_dict)
    if request:
        return url_manager.link
    return LinkSchema().dump(url_manager.link).data


def unshorten(short_url, secret_key=None,
              query_by_code=True, request=None):
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
        if not secret_key or str(link.secret_key) != str(secret_key):
            raise URLAuthFailed(short_url)
    if request:
        save_clickmeta(request, link)
        return link
    return LinkSchema().dump(link).data


def resolve_short(short_code, request=None, secret_key=None):
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
    if link.is_protected:
        if not secret_key or str(link.secret_key) != str(secret_key):
            raise URLAuthFailed(short_code)
    # put stats
    if request:
        save_clickmeta(request, link)
    return link.long_url


def link_stats(short_code):
    """Get short link stats"""
    manager = LinkManager()
    short_code = short_code.strip('+')
    link = manager.get_by_code(short_code=short_code)
    return link if link is None else formatted_link_stats(link)


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
    click_info = {
        'total_hits': click_meta.get('hits', 0),
        'country_stats': click_meta.get('country_hits', {}),
        'referrer': click_meta.get('referrer_hits', {}),
        'time_series_base': click_meta.get('time_base'),
        'time_stats': click_meta.get('timestamp_hits', {}),
    }

    # Hide original/long_url in case of protected links
    if link.is_protected is True:
        link_info['long_url'] = ''
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


def click(short_code):
    """Add method to mimic click url"""
