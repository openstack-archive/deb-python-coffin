from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^url_test/', include('urls_app.urls')),
)
