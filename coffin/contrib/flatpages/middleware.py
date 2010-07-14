import inspect

from django.contrib.flatpages.middleware import *
from coffin.contrib.flatpages.views import flatpage

exec inspect.getsource(FlatpageFallbackMiddleware)\
