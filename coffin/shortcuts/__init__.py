from django.http import HttpResponse
from django.shortcuts import *
from django.template.context import Context as DjangoContext

from coffin.common import dict_from_django_context, get_env


__all__ = ('render_template', 'render_to_response',)


def render_template(template_name, dictionary=None, context_instance=None):
    """
    # TODO: Not quite sure if this is the right approach - we need to
    provide some generic way to render a Jinja template using a
    RequestContext though, for instances where a full render_to_response
    is not appropriate (e.g. custom HTTP Response class).
    Instead, implementing the Django's Template() class on top of Jinja
    might be the way to go. This would also easily allow rendering
    templates from strings with the Coffin environment setup, which
    currently must be done via get_env().

    :param template_name: Filename of the template to get or a sequence of
        filenames to try, in order.
    :param dictionary: Rendering context for the template.
    :returns: A response object with the evaluated template as a payload.
    """
    template = get_env().get_template(template_name)
    dictionary = dictionary or {}
    if isinstance(dictionary, DjangoContext):
        dictionary = dict_from_django_context(dictionary)
    assert isinstance(dictionary, dict) # Required for **-operator.
    if context_instance:
        dictionary.update(dict_from_django_context(context_instance))
    return template.render(**dictionary)


def render_to_response(template_name, dictionary=None, context_instance=None,
                       mimetype=None):
    """
    :param template_name: Filename of the template to get or a sequence of
        filenames to try, in order.
    :param dictionary: Rendering context for the template.
    :returns: A response object with the evaluated template as a payload.
    """
    rendered = render_template(template_name, dictionary, context_instance)
    return HttpResponse(rendered, mimetype=mimetype)
