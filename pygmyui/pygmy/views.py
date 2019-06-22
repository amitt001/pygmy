import json
import string
import operator

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.conf import settings
from utils import pygmy_client_object
from restclient.errors import ObjectNotFound, UnAuthorized, LinkExpired, \
    InvalidInput
from restclient.error_msg import API_ERROR, INVALID_TOKEN
from iso2full import iso2full

# TODO: [IMP] middleware to return 500 page when internal error occurs.
AUTH_COOKIE_NAME = settings.AUTH_COOKIE_NAME
MAX_SHORT_CODE_LEN = 8
INVALID_CUSTOM_CODE_ERROR = ("Invalid value. Length should be <= 8 and should"
                             " be a valid alphabat, digit or a mix of both")
VALID_INPUT_CHARS = string.ascii_letters + string.digits


class URLForm(forms.Form):
    long_url = forms.URLField(help_text='Long Link To Shorten',
                              label='Long URL')
    custom_url = forms.CharField(required=False, label='Custom URL')
    remember_time = forms.IntegerField(required=False,
                                       label='Link Expire Time')
    remember_check = forms.BooleanField(required=False)
    secret_key = forms.CharField(required=False, label='Secret Key')
    secret_check = forms.BooleanField(required=False)

    def clean(self):
        data = self.cleaned_data
        secret_key, custom_url = data.get('secret_key'), data.get('custom_url')
        validation_items = dict(secret_key=secret_key, custom_url=custom_url)
        for k, val in validation_items.items():
            if len(val) > MAX_SHORT_CODE_LEN:
                self.add_error(k, INVALID_CUSTOM_CODE_ERROR)
            for c in val:
                if c not in VALID_INPUT_CHARS:
                    self.add_error(k, INVALID_CUSTOM_CODE_ERROR)
                    break


def link_shortener(request):
    pygmy_client = pygmy_client_object(settings, request)
    if request.method == 'POST':
        form = URLForm(request.POST)
        context = dict(form=form)
        if form.is_valid():
            try:
                resp = pygmy_client.shorten(
                    long_url=form.cleaned_data['long_url'],
                    custom_code=form.cleaned_data['custom_url'],
                    secret=form.cleaned_data['secret_key'],
                    expire_after=form.cleaned_data['remember_time']
                )
            except UnAuthorized as e:
                return render(request,
                              'unauthorized.html',
                              context=API_ERROR(e.args[0]),
                              status=401)
            except (ObjectNotFound, InvalidInput) as e:
                return render(request, '400.html',
                              context=API_ERROR(e.args[0]), status=400)
            short_code = resp['short_code']
        else:
            return render(
                request, "invalid_form.html", context=context, status=400)
        return redirect('get_short_link', code=short_code)

    if request.method == 'GET':
        return render(request, '400.html', status=400)


def get_short_link(request, code):
    """TODO: Validate code"""
    if request.method == 'GET':
        try:
            # TODO: use urljoin
            schema = 'https://' if request.is_secure() else 'http://'
            url_obj = {}
            url_obj['short_url'] = (
                schema + request.META['HTTP_HOST'] + '/' + url_obj.get(
                    'short_code', code)
            )
        except ObjectNotFound as e:
            return render(request, '404.html',
                          context=API_ERROR(e.args[0]), status=404)
        context = dict(short_url=url_obj['short_url'], short_code=code)
        return render(request, 'pygmy/short_url.html', context=context)
    return render(request, '400.html', status=400)


def link_unshorten(request, code):
    """This redirects to the long URL from short URL"""
    pygmy_client = pygmy_client_object(settings, request)
    if request.method == 'GET':
        try:
            url_obj = pygmy_client.unshorten(code)
        except UnAuthorized:
            return redirect('/link/secret?next={}'.format(code))
        except (LinkExpired, ObjectNotFound) as e:
            return render(request, '404.html',
                          context=API_ERROR(e.args[0]), status=404)
        long_url = url_obj['long_url']
        return redirect(long_url, permanent=True)


def short_link_stats(request, code):
    """Get stats about short code."""
    pygmy_client = pygmy_client_object(settings, request)
    if request.method == 'GET':
        try:
            clickmeta = pygmy_client.link_stats(code)
            clickmeta['country_stats'] = sorted(
                clickmeta['country_stats'].items(),
                key=operator.itemgetter(1),
                reverse=True)

            country_stats = [(country, iso2full.get(country, "unknown"), hits)
                             for (country, hits) in clickmeta['country_stats']]
            clickmeta['country_stats'] = country_stats

            clickmeta['referrer'] = sorted(
                clickmeta['referrer'].items(),
                key=operator.itemgetter(1),
                reverse=True)

            context = dict(clickmeta=clickmeta)
        except (ObjectNotFound, LinkExpired) as e:
            return render(request, '404.html',
                          context=API_ERROR(e.args[0]), status=404)
        return render(request, 'pygmy/link_stats.html', context=context)


def link_auth(request):
    """View for handeling protected short links"""
    if request.method == 'GET':
        code = request.GET.get('next')
        if not code:
            return redirect('400.html')
        return render(request, 'auth/link_auth.html')

    if request.method == 'POST':
        pygmy_client = pygmy_client_object(settings, request)
        data = json.loads(request.body.decode('utf-8'))
        code = data['code']
        secret_key = data['secret_key']
        if not code or not secret_key:
            return render(request, '400.html', status=400)
        try:
            if code.startswith('+') or code.endswith('+'):
                clickmeta = pygmy_client.link_stats(
                    code, secret_key=secret_key)
                response = dict(clickmeta=clickmeta)
            else:
                url_obj = pygmy_client.unshorten(code, secret=secret_key)
                response = dict(long_url=url_obj['long_url'])
        except UnAuthorized:
            response = dict(error='Wrong secret key.')
        except ObjectNotFound as e:
            return render(
                request, '404.html', context=API_ERROR(e.args[0]), status=404)
        # return redirect(long_url, permanent=True)
        return JsonResponse(response)


def dashboard(request):
    """Returns the list of signed up user links"""
    access_token = request.COOKIES.get(AUTH_COOKIE_NAME)
    if not access_token:
        return render(request, '400.html', context=INVALID_TOKEN, status=400)
    pygmy_client = pygmy_client_object(settings, request)
    try:
        links = pygmy_client.list_links(access_token=access_token)
    except UnAuthorized as e:
        return render(request,
                      'unauthorized.html',
                      context=API_ERROR(e.args[0]),
                      status=403)
    except ObjectNotFound as e:
        return render(
            request, '404.html', context=API_ERROR(e.args[0]), status=404)
    context = dict(links=links)
    return render(request, 'pygmy/dashboard.html', context=context)


def index(request):
    """Index page"""
    response = render(request, 'pygmy/index.html')
    if (request.COOKIES.get(AUTH_COOKIE_NAME) and
            request.COOKIES.get('refresh_token')):
        pygmy_client = pygmy_client_object(settings, request)
        access_token = pygmy_client.refresh_access_token()
        response.set_cookie(
            AUTH_COOKIE_NAME, access_token.get(AUTH_COOKIE_NAME))
    return response


def check_available(request):
    custom_code = request.GET.get('custom_code')
    if not custom_code:
        return JsonResponse(dict(ok=False))
    pygmy_client = pygmy_client_object(settings, request)
    is_available = pygmy_client.is_available(custom_code)
    return JsonResponse(dict(ok=is_available))
