import inspect

from django.contrib.flatpages.views import *

from coffin.shortcuts import render_to_response
from coffin.template import RequestContext, loader

exec inspect.getsource(flatpage)
