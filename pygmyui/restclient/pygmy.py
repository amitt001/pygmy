"""Pygmy REST api client"""
import requests

from restclient.base import Client, catch_connection_error
from restclient.errors import (
    ObjectNotFound, UnAuthorized, LinkExpired, InvalidInput)
from urllib.parse import urlparse

__all__ = [
    'PygmyApiClient'
]

AUTH_COOKIE_NAME = 'access_token'
REFRESH_COOKIE_NAME = 'refresh_token'


class PygmyApiClient(Client):
    """Pygmy REST API wrapper class"""

    def __init__(self, rest_url, username, password, hostname, request=None):
        """
        Arguments:
            rest_url {[type]} -- Pygmy API url
            username {[type]} -- api username
            password {[type]} -- api password
            hostname {[type]} -- the pygmy website/ui hostname. Used to create the short url
        """

        self.name = username
        self.password = password
        self.rest_url = rest_url
        scheme = 'http://' if not urlparse(hostname).scheme else ''
        self.HOSTNAME = '{}{}'.format(scheme, hostname)
        self.request = request
        self.cookies = None if request is None else request.COOKIES
        super().__init__(rest_url, basic_auth=True, username=username, password=password)

    def __repr__(self):
        return '<PygmyApiClient ({0.name}:{0.password}) {0.rest_url}>'.format(
            self)

    @property
    def header(self):
        _header = dict()
        if self.request is None:
            return _header
        if self.cookies and self.cookies.get(AUTH_COOKIE_NAME):
            _header = dict(JWT_Authorization='Bearer {}'.format(
                self.cookies.get(AUTH_COOKIE_NAME)))
        remote_addr = self.request.META.get('REMOTE_ADDR')
        _header['Pygmy-App-User-Ip'] = self.request.META.get(
                                            'HTTP_X_REAL_IP', remote_addr)
        _header['Pygmy-Http-Rreferrer'] = self.request.META.get('HTTP_REFERER')
        _header['Pygmy-Http-User-Agent'] = self.request.META.get(
            'HTTP_USER_AGENT')
        _header['Pygmy-Header-Key'] = 'KJ*57*6)(*&^dh'
        return _header

    @property
    def refresh_header(self):
        if self.cookies and self.cookies.get(REFRESH_COOKIE_NAME):
            return dict(JWT_Authorization='Bearer {}'.format(
                self.cookies.get(REFRESH_COOKIE_NAME)))

    @catch_connection_error
    def refresh_access_token(self):
        access_token = None
        url_path = self.rest_url + '/token/refresh'
        resp = requests.post(url_path, headers=self.refresh_header)
        if resp.status_code == 401:
            self.request.COOKIES[REFRESH_COOKIE_NAME] = None
            self.request.COOKIES[AUTH_COOKIE_NAME] = None
        if resp.status_code == 200:
            access_token = resp.json()[AUTH_COOKIE_NAME]
            self.cookies[AUTH_COOKIE_NAME] = access_token
            self.request.COOKIES[AUTH_COOKIE_NAME] = access_token
        return {AUTH_COOKIE_NAME: access_token}

    @catch_connection_error
    def ping(self):
        r = requests.get(self.rest_url, headers=self.header)
        if r.status_code // 100 == 2:
            return 'PONG'

    @catch_connection_error
    def shorten(self, long_url, custom_code=None, description=None,
                owner=None, secret=None, expire_after=None):
        """Create the post payload for create short URL REST API.
        :param long_url:
        :param custom_code:
        :param description:
        :param owner:
        :param secret:
        :param expire_after:
        :return:
        """
        url_path = '/api/shorten'
        payload = dict(long_url=long_url,
                       short_code=custom_code,
                       is_custom=custom_code is not None and custom_code != '',
                       description=description,
                       is_protected=secret is not None and secret != '',
                       expire_after=expire_after,
                       secret_key=secret,
                       owner=owner)
        r = self.call(url_path, data=payload, return_for_status=401)
        resp = r.json()
        if int(r.status_code) == 401:
            if resp['sub_status'] == 101:
                self.refresh_access_token()
                if self.header is None:
                    raise UnAuthorized('Please login again to continue')
                r = self.call(url_path, data=payload)
                resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.makeurl(self.HOSTNAME, resp['short_code'])
        return resp

    @catch_connection_error
    def get_longurl_data(self, long_url):
        """
        :param long_url:
        :return:
        """
        url_path = '/api/shorten?url=' + long_url
        r = requests.get(self.rest_url + url_path, headers=self.header)
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        return r.json()

    @catch_connection_error
    def unshorten(self, short_url_code, secret=None):
        """
        :param short_url_code:
        :param secret:
        :return:
        """
        short_code = urlparse(short_url_code).path.strip('/')
        url_path = '/api/unshorten?url=' + self.rest_url + '/' + short_code
        r = self.call(url_path, headers=dict(secret_key=secret))
        resp = r.json()
        if resp.get('short_code'):
            resp['short_url'] = self.makeurl(self.HOSTNAME, resp['short_code'])
        return resp

    @catch_connection_error
    def login(self, email, password):
        """User login"""
        url_path = '/api/login'
        payload = dict(email=email, password=password)
        r = self.call(url_path, data=payload)
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.makeurl(self.HOSTNAME, resp['short_code'])
        return resp

    @catch_connection_error
    def signup(self, data):
        """Signup
        :param data:
        :return: dict
        """
        _ = data.pop('confirm_password')
        url_path = '/api/user'
        r = self.call(url_path, data=data)
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.makeurl(self.HOSTNAME, resp['short_code'])
        return resp

    @catch_connection_error
    def list_links(self, access_token):
        """List of all user links.
        :param access_token:
        :return: dict
        """
        user_path = '/api/user/links'
        headers = self.header
        headers.update(
            dict(JWT_Authorization='Bearer {}'.format(access_token)))
        r = requests.get(self.rest_url + user_path, headers=headers)
        resp_obj = r.json()
        if int(r.status_code) == 401:
            if resp_obj['sub_status'] == 101:
                self.refresh_access_token()
                if self.header is None:
                    raise UnAuthorized('Please login again to continue')
                r = requests.get(self.rest_url + user_path,
                                 headers=self.header)
                resp_obj = r.json()
        if r.status_code // 100 != 2:
            if r.status_code == 401:
                return UnAuthorized('Please login again to continue')
            raise ObjectNotFound(resp_obj)
        links = resp_obj
        for link in links:
            if link.get('short_code'):
                link['short_url'] = self.makeurl(
                    self.HOSTNAME, link['short_code'])
        return links

    @catch_connection_error
    def is_available(self, short_code):
        """Pass a short url code and it tells weather that is available
        or not.

        :param short_code:
        :return: bool
        """
        try:
            resp = self.unshorten(short_code)
            available = not(resp is not None)
        except (UnAuthorized, LinkExpired):
            available = False
        except ObjectNotFound:
            available = True
        return available

    @catch_connection_error
    def link_stats(self, short_code, secret_key=None):
        """Pass a short url code and it returns the stats of of the url.

        :param short_code:
        :param secret_key:
        :return: dict
        """
        # make sure + is added in the code
        short_code = urlparse(short_code).path.strip('/')
        short_code = short_code.strip('+') + '+'
        headers = self.header
        headers.update(dict(secret_key=secret_key))
        r = self.call(short_code, return_for_status=401)
        resp = r.json()
        if int(r.status_code) == 401:
            if resp['sub_status'] == 101:
                self.refresh_access_token()
                if self.header is None:
                    raise UnAuthorized('Please login again to continue')
                r = self.call(short_code)
                resp = r.json()
        if resp.get('short_code'):
            resp['short_url'] = self.makeurl(self.HOSTNAME, resp['short_code'])
        return resp
