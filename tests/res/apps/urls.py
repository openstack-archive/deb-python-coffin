from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^url_test/', include('urls_app.urls')),

    # These two are used to test that our url-tag implementation can
    # deal with application namespaces / the "current app".
    (r'^app/one/', include('urls_app.urls', app_name="testapp", namespace="testapp")),  # default instance
    (r'^app/two/', include('urls_app.urls', app_name="testapp", namespace="two")),
)
