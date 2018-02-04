"""A common util file to use methods across different django apps"""

from restclient import PygmyApiClient
from urllib.parse import urlparse


def make_url(url_address):
    parsed = urlparse(url_address)
    scheme = 'http://' if not parsed.scheme else ''
    return '{}{}'.format(scheme, url_address)


def pygmy_client_object(config, request):
    rest_user = config.PYGMY_API_USER
    rest_pass = config.PYGMY_API_PASSWORD
    rest_url = make_url(config.PYGMY_API_ADDRESS)
    hostname = config.HOSTNAME
    return PygmyApiClient(rest_url, rest_user, rest_pass, hostname, request)

