from django.http import HttpResponse
from django.shortcuts import *
from django.template.context import Context as DjangoContext

from coffin.common import dict_from_django_context, get_env


def render_to_response(template_name, dictionary=None, context_instance=None,
                       mimetype=None):
    """
    :param template_name: Filename of the template to get or a sequence of
        filenames to try, in order.
    :param dictionary: Rendering context for the template.
    :returns: A response object with the evaluated template as a payload.
    """
    template = get_env().get_template(template_name)
    if isinstance(dictionary, DjangoContext):
        dictionary = dict_from_django_context(dictionary)
    assert isinstance(dictionary, dict) # Required for **-operator.
    if context_instance:
        dictionary.update(dict_from_django_context(context_instance))
    rendered = template.render(**dictionary)
    return HttpResponse(rendered, mimetype=mimetype)
