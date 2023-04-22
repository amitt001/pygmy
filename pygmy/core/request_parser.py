"""Fetch info from the short url click"""
from pygmy.core.logger import log

try:
    # Optional package
    import geoip2.database
except Exception:
    log.exception("ModuleNotFoundError: No module named 'geoip2'")

def parse_request(request):
    """Pass request object and returns parsed data dict.
    Country is fetched from IP using maxmind db.

    :param request:
    :return:
    """
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    data = dict(
        referrer=request.referrer,
        user_agent=request.headers.get("User-Agent"),
        country=ip_country(ip)
    )
    return data


def parse_header(request):
    """Pass request object and returns parsed data dict.
    Country is fetched from IP using maxmind db.

    :param request:
    :return:
    """
    ip = request.headers.get('Pygmy-App-User-Ip')
    data = dict(
        referrer=request.headers.get('Pygmy-Http-Rreferrer'),
        user_agent=request.headers.get('Pygmy-Http-User-Agent'),
        country=ip_country(ip)
    )
    return data


def ip_country(ip):
    """Get country from ip. Uses Geoip2 db.

    :param ip:
    :return: None/str
    """
    c_iso_code = None
    try:
        reader = geoip2.database.Reader('pygmy/app/GeoLite2-Country.mmdb')
        c = reader.country(ip)
        c_iso_code = c.country.iso_code
    except Exception as e:
        log.error(e)
    return c_iso_code
