"""Pygmy REST api client"""
import requests

from functools import wraps
from restclient.errors import ObjectNotFound, RestAPIConnectionError, \
    UnAuthorized, LinkExpired


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

    def __init__(self, config):
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

    @catch_connection_error
    def ping(self):
        r = requests.get(self.rest_url)
        if r.status_code // 100 == 2:
            return 'PONG'

    @catch_connection_error
    def shorten(
            self, long_url, custom_url=None, description=None,
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
        r = requests.post(self.rest_url + url_path, json=payload)
        if int(r.status_code // 100) != 2:
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
        r = requests.get(self.rest_url + url_path)
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        return r.json()

    @catch_connection_error
    def unshorten(self, short_url_code, secret_key=None, hit_counter=False):
        """
        :param short_url_code:
        :param secret_key:
        :param hit_counter:
        :return:
        """
        url_path = '/api/unshorten?url=' + self.rest_url + '/' + short_url_code
        url_path += '&hit_counter={}'.format(True)
        r = requests.get(self.rest_url + url_path,
                         headers=dict(secret_key=secret_key))
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
        r = requests.post(self.rest_url + url_path, json=payload)
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
        r = requests.post(self.rest_url + url_path, json=data)
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        resp = r.json()
        if resp.get('short_url'):
            resp['short_url'] = self.HOSTNAME + '/' + resp['short_code']
        return resp

    @catch_connection_error
    def list_links(self, user_id, access_token):
        """List of all user links.
        :param user_id:
        :param access_token:
        :return: dict
        """
        user_path = '/api/user/{}/links'.format(user_id)
        headers = dict(Authorization='Bearer {}'.format(access_token))
        r = requests.get(self.rest_url + user_path, headers=headers)
        if r.status_code // 100 != 2:
            raise ObjectNotFound(r.json())
        links = r.json()
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
