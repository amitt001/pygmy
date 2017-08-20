
from django.conf.urls import url
from django.views.generic.base import TemplateView
from . import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(
                    template_name='pygmy/index.html'), name='index'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^shorten$', views.link_shortener, name='link_shortener'),
    url(r'^shorten/(?P<code>[a-zA-Z0-9]+)$', views.get_short_link,
        name='get_short_link'),
    url(r'^link/secret$', views.link_auth, name='link_auth'),
    url(r'^(?P<code>[a-zA-Z0-9]+)$', views.link_unshorten, name='shorten')
]