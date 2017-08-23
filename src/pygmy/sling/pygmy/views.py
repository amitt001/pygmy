from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.conf import settings
from restclient.pygmy import PygmyApiClient
from restclient.errors import ObjectNotFound, UnAuthorized, LinkExpired
from restclient.error_msg import *

# TODO: [IMP] middleware to return 500 page when internal error occurs.
_SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME


class URLForm(forms.Form):
    long_url = forms.URLField(help_text='Long Link To Shorten',
                              label='Long URL')
    custom_url = forms.CharField(required=False, label='Custom URL')
    remember_time = forms.IntegerField(required=False,
                                       label='Link Expire Time')
    remember_check = forms.BooleanField(required=False)
    secret_key = forms.CharField(required=False, label='Secret Key')
    secret_check = forms.BooleanField(required=False)


def link_shortener(request):
    pygmy_client = PygmyApiClient(settings)
    if request.method == 'POST':
        form = URLForm(request.POST)
        context = dict(form=form)
        if form.is_valid():
            owner = request.session.get('user', {}).get('id')
            if owner:
                owner = owner.split('/')[-1]
            try:
                resp = pygmy_client.shorten(
                    long_url=form.cleaned_data['long_url'],
                    custom_url=form.cleaned_data['custom_url'],
                    secret=form.cleaned_data['secret_key'],
                    expire_after=form.cleaned_data['remember_time'],
                    owner=owner
                )
            except ObjectNotFound as e:
                return render(request, 'pygmy/400.html',
                              context=API_ERROR(e.args[0]))
            short_code = resp['short_code']
        else:
            return render(request, 'pygmy/short_url.html', context=context)
        return redirect('get_short_link', code=short_code)

    if request.method == 'GET':
        return render(request, 'pygmy/400.html')


def get_short_link(request, code):
    """TODO: Validate code"""
    pygmy_client = PygmyApiClient(settings)
    if request.method == 'GET':
        try:
            url_obj = pygmy_client.unshorten(code)
            url_obj['short_url'] = (
                request.META['HTTP_HOST'] + '/' + url_obj['short_code'])
        except ObjectNotFound as e:
            return render(request, 'pygmy/404.html',
                          context=API_ERROR(e.args[0]))
        context = dict(
            short_url=url_obj['short_url'],
            long_url=url_obj['long_url'])
        return render(request, 'pygmy/short_url.html', context=context)
    return render(request, 'pygmy/400.html')


def link_unshorten(request, code):
    """This redirects to the long URL from short URL"""
    pygmy_client = PygmyApiClient(settings)
    if request.method == 'GET':
        try:
            url_obj = pygmy_client.unshorten(code, hit_counter=True)
        except UnAuthorized:
            return redirect('/link/secret?next={}'.format(code))
        except LinkExpired:
            return render(request, 'pygmy/404.html')
        except ObjectNotFound as e:
            return render(request, 'pygmy/404.html',
                          context=API_ERROR(e.args[0]))
        long_url = url_obj['long_url']
        return redirect(long_url, permanent=True)


def link_auth(request):
    """View for handeling protected short links"""
    if request.method == 'GET':
        code = request.GET.get('next')
        if not code:
            return redirect('pygmy/400.html')
        return render(request, 'auth/link_auth.html')

    if request.method == 'POST':
        pygmy_client = PygmyApiClient(settings)
        data = json.loads(request.body.decode('utf-8'))
        code = data['code']
        secret_key = data['secret_key']
        if not code or not secret_key:
            return render(request, 'pygmy/400.html')
        try:
            url_obj = pygmy_client.unshorten(code, secret_key=secret_key)
            response = dict(long_url=url_obj['long_url'])
        except UnAuthorized:
            response = dict(message='Wrong secret key.')
        except ObjectNotFound as e:
            return render(
                request, 'pygmy/404.html', context=API_ERROR(e.args[0]))
        # return redirect(long_url, permanent=True)
        return JsonResponse(response)


def dashboard(request):
    """Returns the list of signed up user links"""
    access_token = request.session.get(_SESSION_COOKIE_NAME)
    if not access_token:
        return render(request, 'pygmy/404.html', context=INVALID_TOKEN)
    pygmy_client = PygmyApiClient(settings)
    user_link = request.session.get('user').get('id')
    user_id = user_link.split('/')[-1]
    try:
        links = pygmy_client.list_links(
            user_id=user_id, access_token=access_token)
    except ObjectNotFound as e:
        return render(request, 'pygmy/404.html', context=API_ERROR(e.args[0]))
    context = dict(links=links)
    return render(request, 'pygmy/dashboard.html', context=context)


def check_available(request):
    custom_code = request.GET.get('custom_code')
    if not custom_code:
        return JsonResponse(dict(ok=False))
    pygmy_client = PygmyApiClient(settings)
    is_available = pygmy_client.is_available(custom_code)
    return JsonResponse(dict(ok=is_available))
