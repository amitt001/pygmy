"""Process response middleware. Used for two:

1. Seting new refreshed access token to response
2. Logout user if refresh_token has expired"""
from django.conf import settings


class ResponseMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        # Check if user is logged in and refresh_token has expired
        if (request.COOKIES.get('f_name') and
            request.COOKIES.get(settings.REFRESH_COOKIE_NAME) is None):
            cookie_keys = ['f_name', 'email',
                           settings.AUTH_COOKIE_NAME,
                           settings.REFRESH_COOKIE_NAME]
            _ = [response.delete_cookie(key=k) for k in cookie_keys]
        elif request.COOKIES.get(settings.AUTH_COOKIE_NAME):
            response.set_cookie(
                settings.AUTH_COOKIE_NAME, request.COOKIES['access_token'])
        return response

