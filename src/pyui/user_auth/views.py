# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from utils import pygmy_client_object
from restclient.error_msg import API_ERROR
from restclient.errors import ObjectNotFound, InvalidInput

AUTH_COOKIE_NAME = settings.AUTH_COOKIE_NAME
REFRESH_COOKIE_NAME = settings.REFRESH_COOKIE_NAME


class LoginForm(forms.Form):
    email = forms.EmailField(label='Long URL', required=True,
                             help_text='Please include a valid email address.')
    password = forms.CharField(max_length=24, required=True)
    remember = forms.BooleanField(required=False)


class SignUpForm(forms.Form):
    f_name = forms.CharField(required=True, label='First Name')
    l_name = forms.CharField(required=True, label='Last Name')
    email = forms.EmailField(
        required=True, label='Email ID',
        help_text='Please include a valid email address.')
    password = forms.CharField(max_length=24, required=True)
    confirm_password = forms.CharField(max_length=24, required=True,
                                       label='Password')

    def clean(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('confirm_password')
        if p1 and p1 != p2:
            raise forms.ValidationError(dict(password='Password mismatch'))


def login(request):
    if request.method == 'POST':
        pygmy_client = pygmy_client_object(settings, request)
        form = LoginForm(request.POST)
        context = dict(form=form)
        if form.is_valid():
            context['login_success'] = True
            try:
                user_obj = pygmy_client.login(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'])
                context = {'email': user_obj['email'],
                           'f_name': user_obj['f_name'],
                           REFRESH_COOKIE_NAME: user_obj['refresh_token']}
            except InvalidInput as e:
                return render(request, 'unauthorized.html',
                              context=API_ERROR(e.args[0]), status=400)
            except ObjectNotFound as e:
                return render(request, '404.html',
                              context=API_ERROR(e.args[0]), status=404)
            response = redirect('dashboard')
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            _ = [response.set_cookie(
                    k, v, expires=expires) for k, v in context.items()]
            # access token lifetime till browser session
            response.set_cookie(AUTH_COOKIE_NAME, user_obj['access_token'])
        else:
            response = render(
                request, "invalid_form.html", context=context, status=400)
        return response

    if request.method == 'GET':
        return redirect('/')


def logout(request):
    if request.method == 'GET':
        response = redirect('/')
        cookie_keys = ['f_name', 'email', AUTH_COOKIE_NAME, REFRESH_COOKIE_NAME]
        for k in cookie_keys:
            response.delete_cookie(key=k)
        return response


def signup(request):
    if request.method == 'GET':
        return redirect('/')

    if request.method == 'POST':
        pygmy_client = pygmy_client_object(settings, request)
        form = SignUpForm(request.POST)
        context = dict(form=form)
        if not form.is_valid():
            return render(request, "invalid_form.html", context=context, status=400)
        context['signup_success'] = True
        try:
            user_obj = pygmy_client.signup(form.cleaned_data)
            context = {'email': user_obj['email'],
                       'f_name': user_obj['f_name'],
                       REFRESH_COOKIE_NAME: user_obj['refresh_token']}
        except (InvalidInput, ObjectNotFound) as e:
            return render(request, '400.html',
                          context=API_ERROR(e.args[0]), status=400)
        response = redirect('/')
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        _ = [response.set_cookie(
                k, v, expires=expires) for k, v in context.items()]
        # access token lifetime till browser session
        response.set_cookie(AUTH_COOKIE_NAME, user_obj['access_token'])
        return response
