import os
import sys
import requests
import logging

from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
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

logger = logging.getLogger(__name__)


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

    def __init__(
            self, base_url, basic_auth=False, username=None, password=None,
            request_data_type='json', return_for_status=[]):
        """Pass username and password as None when basic auth is disabled"""
        self.rest_url = base_url
        self.basic_auth = None
        self.request_data_type = request_data_type
        if return_for_status and not isinstance(return_for_status, list):
            return_for_status = [return_for_status]
        self.return_for_status = return_for_status

        if basic_auth is True:
            if password is None or username is None:
                raise RestClientException(
                    '`username` and `password` are required when `basic_auth` is True'
                )
            self.basic_auth = requests.auth.HTTPBasicAuth(username, password)

    @property
    def header(self):
        raise NotImplementedError

    @staticmethod
    def makeurl(base_url, path):
        return urljoin(base_url, path)

    def call(self, path, data=None, method=None,
             return_for_status=[], headers=None):
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
        :param headers: Add parameters to header
        :type headers: dict
        :return:
        """
        header_params = self.header
        header_params.update({'User-Agent': 'Pygmy API REST client'})
        if headers:
            header_params.update(headers)

        request_param = dict(
            url=self.makeurl(self.rest_url, path), auth=self.basic_auth, headers=header_params
        )

        _call = requests.get
        if method is None:
            method = 'GET' if data is None else 'POST'
        if method.upper() == 'POST':
            _call = requests.post
            if self.request_data_type == 'json':
                request_param['json'] = data
            else:
                request_param['data'] = data
        # Make rest call and handle the response
        response = _call(**request_param)

        if return_for_status and not isinstance(return_for_status, list):
            return_for_status = [return_for_status]
        return_for_status = self.return_for_status + return_for_status
        if response.status_code in return_for_status:
            return response

        error_object = self.error_object_from_response(response)
        if error_object is not None:
            logger.debug('Reveived error response: %s', response.text)
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


