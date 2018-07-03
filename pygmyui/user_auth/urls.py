from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views


urlpatterns = [
    url(r'^signup$', views.signup, name='signup'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
]