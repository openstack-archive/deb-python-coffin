import inspect

from django.contrib.auth import urls

exec inspect.getsource(urlpatterns)\
        .replace('django.contrib.auth.views', 'coffin.contrib.auth.views')