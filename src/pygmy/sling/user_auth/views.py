# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from restclient.pygmy import PygmyApiClient
from restclient.error_msg import API_ERROR
from restclient.errors import ObjectNotFound

_SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME


class LoginForm(forms.Form):
    email = forms.EmailField(help_text='Long Link To Shorten',
                             label='Long URL')
    password = forms.CharField(max_length=24, required=True)
    remember = forms.BooleanField(required=False)


class SignUpForm(forms.Form):
    f_name = forms.CharField(required=True)
    l_name = forms.CharField(required=True)
    email = forms.EmailField(help_text='Long Link To Shorten',
                             label='Long URL', required=True)
    password = forms.CharField(max_length=24, required=True)
    confirm_password = forms.CharField(max_length=24, required=True)

    def clean(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('confirm_password')
        if p1 and p1 != p2:
            raise forms.ValidationError('Password mismatch')


def login(request):
    if request.method == 'POST':
        pygmy_client = PygmyApiClient(settings)
        form = LoginForm(request.POST)
        context = dict(form=form)
        if form.is_valid():
            context['login_success'] = True
            try:
                context = pygmy_client.login(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'])
            except ObjectNotFound as e:
                return render(request, 'pygmy/404.html',
                              context=API_ERROR(e.args[0]))
            request.session[_SESSION_COOKIE_NAME] = context.get('access_token')
            # response = render(
            #     request, "auth/login_status.html", context=context)
            response = redirect('dashboard')
            request.session['user'] = context
        else:
            response = render(request, "pygmy/400.html")
        return response

    if request.method == 'GET':
        return redirect('/')


def logout(request):
    if request.method == 'GET':
        response = redirect('/')
        response.delete_cookie(key=_SESSION_COOKIE_NAME)
        return response


def signup(request):
    if request.method == 'GET':
        return redirect('/')

    if request.method == 'POST':
        pygmy_client = PygmyApiClient(settings)
        form = SignUpForm(request.POST)
        context = dict(form=form)
        if not form.is_valid():
            return render(request, "pygmy/400.html")
        context['signup_success'] = True
        try:
            context = pygmy_client.signup(form.cleaned_data)
        except ObjectNotFound as e:
            return render(request, 'pygmy/400.html',
                          context=API_ERROR(e.args[0]))
        request.session[_SESSION_COOKIE_NAME] = context.get('access_token')
        request.session['user'] = context
        return redirect('/')
