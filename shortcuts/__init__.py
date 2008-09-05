from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404

from coffin.template import loader
from coffin.common import MIMETYPE_KEY


__all__ = ('render_to_response', 'get_object_or_404', 'get_list_or_404')


def render_to_response(*args, **kwargs):
    httpresponse_kwargs = {MIMETYPE_KEY: kwargs.pop(MIMETYPE_KEY, None)}
    response_str = loader.render_to_string(*args, **kwargs)
    return HttpResponse(response_str, **httpreponse_kwargs)
