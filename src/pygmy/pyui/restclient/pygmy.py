"""Pygmy REST api client"""
import requests

from functools import wraps
from django.conf import settings
from restclient.errors import ObjectNotFound, RestAPIConnectionError, \
    UnAuthorized, LinkExpired, InvalidInput

AUTH_COOKIE_NAME = settings.AUTH_COOKIE_NAME
REFRESH_COOKIE_NAME = settings.REFRESH_COOKIE_NAME


def catch_connection_error(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            # TODO: Error from the error class not hard coded.
            raise RestAPIConnectionError("Connection to Pygmy API Failed.")

    return _wrapped


class PygmyApiClient:
    """Base class"""

    def __init__(self, config, request=None):
        """
        :param config:
        """
        self.config = config
        # Required parameters
        self.rest_host = config.PYGMY_API_HOST
        self.rest_port = str(config.PYGMY_API_PORT)
        self.rest_auth_type = config.PYGMY_API_AUTH
        self.rest_user = config.PYGMY_API_USER
        self.rest_pass = config.PYGMY_API_PASSWORD
        self.rest_url = 'http://' + self.rest_host + ':' + self.rest_port
        self.HOSTNAME = config.HOSTNAME
        self.request = request
        self.cookies = None if request is None else request.COOKIES

    @property
    def header(self):
        _header = dict()
        if self.cookies and self.cookies.get(AUTH_COOKIE_NAME):
            _header = dict(Authorization='Bearer {}'.format(
                self.cookies.get(AUTH_COOKIE_NAME)))
        _header['Pygmy-App-User-Ip'] = self.request.META.get('REMOTE_ADDR')
        _header['Pygmy-Http-Rreferrer'] = self.request.META.get('HTTP_REFERER')
        _header['Pygmy-Http-User-Agent'] = self.request.META.get(
            'HTTP_USER_AGENT')
        _header['Pygmy-Header-Key'] = 'KJ*57*6)(*&^dh'
        return _header

    @property
    def refresh_header(self):
        if self.cookies and self.cookies.get(REFRESH_COOKIE_NAME):
            return dict(Authorization='Bearer {}'.format(
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
    def shorten(self, long_url, custom_url=None, description=None,
                owner=None, secret=None, expire_after=None):
        """Create the post payload for create short URL REST API.
        :param long_url:
        :param custom_url:
        :param description:
        :param owner:
        :param secret:
        :param expire_after:
        :return:
        """
        url_path = '/api/shorten'
        payload = dict(long_url=long_url,
                       short_code=custom_url,
                       is_custom=custom_url is not None and custom_url != '',
                       description=description,
                       is_protected=secret is not None and secret != '',
                       expire_after=expire_after,
                       secret_key=secret,
                       owner=owner)
        r = requests.post(
            self.rest_url + url_path, json=payload, headers=self.header)
        resp = r.json()
        if int(r.status_code) == 401:
            if resp['sub_status'] == 101:
                self.refresh_access_token()
                if self.header is None:
                    raise UnAuthorized('Please login again to continue')
                r = requests.post(self.rest_url + url_path,
                                  json=payload,
                                  headers=self.header)
        if int(r.status_code // 100) != 2:
            if r.status_code == 401:
                raise UnAuthorized('Please login again to continue')
            if r.status_code == 400:
                raise InvalidInput(r.json())
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
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
    def unshorten(self, short_url_code, secret_key=None):
        """
        :param short_url_code:
        :param secret_key:
        :return:
        """
        url_path = '/api/unshorten?url=' + self.rest_url + '/' + short_url_code
        headers = self.header
        headers.update(dict(secret_key=secret_key))
        r = requests.get(self.rest_url + url_path,
                         headers=headers)
        if r.status_code == 403:
            raise UnAuthorized(r.json())
        if r.status_code == 410:
            raise LinkExpired(r.json())
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
        return resp

    @catch_connection_error
    def login(self, email, password):
        """
        :param email:
        :param password:
        :return:
        """
        url_path = '/api/login'
        payload = dict(email=email, password=password)
        r = requests.post(
            self.rest_url + url_path, json=payload, headers=self.header)
        if r.status_code == 400:
            raise InvalidInput(r.json())
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
        return resp

    @catch_connection_error
    def signup(self, data):
        """Signup
        :param data:
        :return: dict
        """
        _ = data.pop('confirm_password')
        url_path = '/api/user'
        r = requests.post(
            self.rest_url + url_path, json=data, headers=self.header)
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
        return resp

    @catch_connection_error
    def list_links(self, access_token):
        """List of all user links.
        :param access_token:
        :return: dict
        """
        user_path = '/api/user/links'
        headers = self.header
        headers.update(dict(Authorization='Bearer {}'.format(access_token)))
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
            if link.get('short_url'):
                link['short_url'] = self.HOSTNAME + '/' + link['short_code']
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
    def link_stats(self, short_code):
        """Pass a short url code and it returns the stats of of the url.

        :param short_code:
        :return: dict
        """
        # make sure + is added in code
        short_code = short_code.strip('+') + '+'
        r = requests.get(self.rest_url + '/' + short_code, headers=self.header)
        resp = r.json()
        if int(r.status_code) == 401:
            if resp['sub_status'] == 101:
                self.refresh_access_token()
                if self.header is None:
                    raise UnAuthorized('Please login again to continue')
                r = requests.get(self.rest_url + '/' + short_code,
                                 headers=self.header)
        if r.status_code == 403:
            raise UnAuthorized(r.json())
        if r.status_code == 410:
            raise LinkExpired(r.json())
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
        return resp
