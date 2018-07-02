import requests

from functools import wraps
from restclient.errors import (
    RestAPIConnectionError, RestClientException, ObjectNotFound,
    LinkExpired, UnAuthorized, InvalidInput)
from urllib.parse import urljoin


__all__ = [
    'Client',
    'catch_connection_error'
]

BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
RESOURCE_EXPIRED = 410


def catch_connection_error(func):
    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            # TODO: Error from the error class not hard coded.
            raise RestAPIConnectionError("Connection to Pygmy API Failed.")
    return _wrapped


class Client:
    """This is an Abstract Base Class"""

    def __init__(self, rest_url, username, password):
        """Pass username and password as None when basic auth is disabled"""
        self.rest_url = rest_url
        self.basic_auth = None
        if password is None:
            raise RestClientException(
                '`username` is required when `password` is given')
        if username is None:
            raise RestClientException(
                '`password` is required when `username` is given')
        if not (username is None and password is None):
            self.basic_auth = requests.auth.HTTPBasicAuth(username, password)

    @property
    def header(self):
        raise NotImplementedError

    @staticmethod
    def makeurl(base_url, path):
        return urljoin(base_url, path)

    def call(self, path, data=None, method=None,
             return_for_status=[], header_param=None):
        """
        The wrapper over `requests` library.
        :param path: url_path
        :param data: Post data, None in case of GET
        :type data: json/dict
        :param method: None or GET/POST
        :type method: str
        :param return_for_status: Status codes which should be raised instead of
            being handled here, so that calling method can handle it in it's
            own custom way.
        :type return_for_status: str/list
        :param header_param: Add parameters to header
        :type header_param: dict
        :return:
        """
        headers = self.header
        headers.update({'User-Agent': 'Pygmy API REST client'})
        if header_param:
            headers.update(header_param)
        request_param = dict(
            url=self.makeurl(self.rest_url, path),
            auth=self.basic_auth, headers=headers)
        _call = requests.get
        if method is None:
            method = 'GET' if data is None else 'POST'
        if method.upper() == 'POST':
            _call = requests.post
            request_param['json'] = data
        # Make rest call and handle the response
        response = _call(**request_param)
        if return_for_status and not isinstance(return_for_status, list):
            return_for_status = [return_for_status]
        if response.status_code in return_for_status:
            return response
        error_object = self.error_object_from_response(response)
        if error_object is not None:
            raise error_object
        return response

    @staticmethod
    def error_object_from_response(response):
        error_object = None
        if response.status_code == BAD_REQUEST:
            error_object = InvalidInput(response.json())
        elif response.status_code == FORBIDDEN:
            error_object = UnAuthorized(response.json())
        elif response.status_code == RESOURCE_EXPIRED:
            error_object = LinkExpired(response.json())
        elif response.status_code // 100 != 2:
            error_object = ObjectNotFound(response.json())
        return error_object


