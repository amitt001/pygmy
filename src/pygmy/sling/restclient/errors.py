

class RestClientException(Exception):
    pass


class ObjectNotFound(RestClientException):
    pass


class UnAuthorized(RestClientException):
    pass


class LinkExpired(RestClientException):
    pass


class RestAPIConnectionError(RestClientException):
    pass
