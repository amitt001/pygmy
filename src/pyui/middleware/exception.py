"""Exception middleare. Catch all 500 errors and return a simple page"""

import traceback

from django.shortcuts import render


class ExceptionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        if response:
            # if response.status_code == 404:
            #     return render(request, '{}.html'.format(response.status_code))
            # if response.status_code//100 == 4:
            #     return render(request, '400.html', status=400)
            pass
        return response

    def process_exception(self, request, exception):
        if exception is not None:
            traceback.print_exc()
            return render(request, '500.html', status=500)
