import ipaddress
import re

from marshmallow import ValidationError
from pygmy.config import config
from urllib.parse import urljoin, urlparse

filtered_urls = [
    'pygy.co',
    'bit.ly'
    'rb.gy',
    'tinyurl.com',
    'ow.ly',
    'is.gd'
]

# RFC 1918 private ranges, loopback, link-local (e.g. AWS metadata),
# and other reserved blocks that must never be reachable via a shortener.
_BLOCKED_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),       # RFC 1918 private
    ipaddress.ip_network('172.16.0.0/12'),     # RFC 1918 private
    ipaddress.ip_network('192.168.0.0/16'),    # RFC 1918 private
    ipaddress.ip_network('127.0.0.0/8'),       # loopback
    ipaddress.ip_network('169.254.0.0/16'),    # link-local / cloud metadata
    ipaddress.ip_network('0.0.0.0/8'),         # unspecified
    ipaddress.ip_network('::1/128'),           # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),          # IPv6 unique local
    ipaddress.ip_network('fe80::/10'),         # IPv6 link-local
]

_BLOCKED_HOSTNAMES = {'localhost', 'localhost.localdomain'}


def _is_ssrf_safe(hostname):
    """Return False if the hostname resolves to a private/reserved address.

    Blocks:
    - 'localhost' and common loopback aliases
    - Any bare IP literal that falls within a reserved network range
    Public domain names (e.g. 'example.com') pass through; DNS resolution is
    intentionally *not* performed here to avoid latency — that is a separate
    runtime concern.
    """
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        return False
    # Strip IPv6 brackets: [::1] -> ::1
    bare = hostname.strip('[]')
    try:
        addr = ipaddress.ip_address(bare)
        for network in _BLOCKED_NETWORKS:
            if addr in network:
                return False
    except ValueError:
        # Not a bare IP literal — treat as a public hostname (safe to allow).
        pass
    return True


def validate_url(url):
    """Validate a URL before shortening.

    Rejects:
    - Malformed URLs that don't match the expected http(s)/ftp(s) format
    - URLs targeting private/reserved IP ranges or localhost (SSRF prevention)
    - Already-shortened URLs from known services
    """
    url = url or 'invalid'
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    is_valid = regex.match(url) is not None
    if is_valid:
        parsed = urlparse(url)
        # Block private/reserved hosts to prevent SSRF
        if not _is_ssrf_safe(parsed.hostname or ''):
            raise ValidationError(
                'URLs pointing to private or reserved addresses are not allowed.')
        allowed_path = ['contact', 'about', 'shorten', 'dashboard']
        if parsed.netloc == 'pygy.co' and parsed.path.strip('/') in allowed_path:
            return is_valid
        elif parsed.netloc in filtered_urls and parsed.path.strip('/') not in allowed_path:
            raise ValidationError('Already shortened links are not supported')
        else:
            return is_valid


def make_short_url(short_path):
    short_url = urljoin('{}{}'.format(config.pygmy['short_url_schema'], config.pygmy['short_url']), short_path)
    return short_url


def get_short_path(short_url):
    parts = urlparse(short_url)
    short_path = parts.path.lstrip('/')
    return short_path
