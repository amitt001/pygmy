"""Demo-only account boundary; self-hosted accounts remain enabled by default."""
from django.conf import settings
from django.shortcuts import render

class DemoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.PYGMY_DEMO_MODE:
            for name in ('access_token', 'refresh_token', 'f_name', 'email'):
                request.COOKIES.pop(name, None)
            if request.path.rstrip('/') in ('/signup', '/login', '/logout', '/dashboard'):
                return render(request, 'auth/demo_disabled.html', status=403)
        return self.get_response(request)
