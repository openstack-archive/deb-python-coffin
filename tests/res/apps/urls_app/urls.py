from django.conf.urls.defaults import *

urlpatterns = patterns('apps.urls_app',
    # Test urls for testing reverse lookups
    url(r'^$', 'views.index', name='the-index-view'),
    (r'^sum/(?P<left>\d+),(?P<right>\d+)$', 'views.sum'),
)
