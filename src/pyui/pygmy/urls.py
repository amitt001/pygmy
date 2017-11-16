
from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^shorten$', views.link_shortener, name='link_shortener'),
    url(r'^shorten/(?P<code>[a-zA-Z0-9]+)$', views.get_short_link,
        name='get_short_link'),
    url(r'^link/secret$', views.link_auth, name='link_auth'),
    url(r'^check$', views.check_available, name='link_available'),
    url(r'^(?P<code>[a-zA-Z0-9]+)$', views.link_unshorten, name='shorten'),
    url(r'^(?P<code>[a-zA-Z0-9+]+)$', views.short_link_stats, name='linkstats')
]