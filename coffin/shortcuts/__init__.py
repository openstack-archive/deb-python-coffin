from django.http import HttpResponse

# Merge with original namespace so user
# doesn't have to import twice.
from django.shortcuts import *


__all__ = ('render_to_string', 'render_to_response', 'render')


# Is within ``template.loader`` as per Django specification -
# but I think it fits very well here.
from coffin.template.loader import render_to_string


def render_to_response(template_name, dictionary=None, context_instance=None,
                       mimetype=None):
    """
    :param template_name: Filename of the template to get or a sequence of
        filenames to try, in order.
    :param dictionary: Rendering context for the template.
    :returns: A response object with the evaluated template as a payload.
    """
    rendered = render_to_string(template_name, dictionary, context_instance)
    return HttpResponse(rendered, mimetype=mimetype)


def render(request, *args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    coffin.template.loader.render_to_string() with the passed arguments.
    Uses a RequestContext by default.
    """
    httpresponse_kwargs = {
        'content_type': kwargs.pop('content_type', None),
        'status': kwargs.pop('status', None),
        }

    if 'context_instance' in kwargs:
        context_instance = kwargs.pop('context_instance')
        if kwargs.get('current_app', None):
            raise ValueError('If you provide a context_instance you must '
                             'set its current_app before calling render()')
    else:
        current_app = kwargs.pop('current_app', None)
        context_instance = RequestContext(request, current_app=current_app)

    kwargs['context_instance'] = context_instance

    return HttpResponse(render_to_string(*args, **kwargs),
                        **httpresponse_kwargs)
