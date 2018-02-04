"""Fetch info from the short url click"""
import geoip2.database

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
    try:
        reader = geoip2.database.Reader('pygmy/app/GeoLite2-Country.mmdb')
        c = reader.country(ip)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
    return c.country.iso_code
