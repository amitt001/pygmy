"""A common util file to use methods across different django apps"""
import os
import logging

from restclient.pygmy import PygmyApiClient

from urllib.parse import urlparse


def make_url(url_address):
    parsed = urlparse(url_address)
    scheme = 'http://' if not parsed.scheme else ''
    return '{}{}'.format(scheme, url_address)


def pygmy_client_object(config, request):
    rest_user = config.PYGMY_API_USER
    rest_pass = config.PYGMY_API_PASSWORD
    pygmy_api_host, pygmy_api_port = urlparse(config.PYGMY_API_ADDRESS).netloc.split(':')

    # Check if PYGMY_API_ADDRESS enviornment varibale is set
    if os.environ.get('PYGMY_API_ADDRESS'):
        pygmy_api_host = os.environ.get('PYGMY_API_ADDRESS')
        logging.info('Using environment variable PYGMY_API_ADDRESS. API URL: %s', pygmy_api_host)

    rest_url = make_url('http://{}:{}'.format(pygmy_api_host, pygmy_api_port))
    hostname = config.HOSTNAME
    return PygmyApiClient(rest_url, rest_user, rest_pass, hostname, request)
