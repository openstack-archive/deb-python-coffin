"""
coffin
~~~~~~

coffin is a package that does its best to resolve the impedance mismatch
between Django and Jinja2 through various adapters. The aim is to use
Djinja2 as a drop-in replacement for Django's template system to whatever
extent is reasonable.

:copyright: 2008 by Christopher D. Leary
:license: BSD, see LICENSE for more details.
"""

__docformat__ = 'restructuredtext en'


from jinja2 import Environment, loaders
from django.template import Context as DjangoContext
from django.conf import settings
from django.http import HttpResponse


def make_app_loader():
    from django.template.loaders.app_directories import app_template_dirs
    return loaders.FileSystemLoader(app_template_dirs)


# Determine loaders from Django's conf.
_JINJA_LOADER_BY_DJANGO_SUBSTR = { # {substr: callable, ...}
    'app_directories': make_app_loader,
}


def jinja_loader_from_django_loader(django_loader):
    for substr, func in _JINJA_LOADER_BY_DJANGO_SUBSTR.iteritems():
        if substr in django_loader:
            return func()


_LOADERS = []
for loader in settings.TEMPLATE_LOADERS:
    if isinstance(loader, basestring):
        loader_obj = jinja_loader_from_django_loader(loader)
        if loader_obj:
            _LOADERS.append(loader_obj)
    else: # It's assumed to be a Jinja2 loader instance.
        _LOADERS.append(loader)


_ENV = Environment(loader=loaders.ChoiceLoader(_LOADERS))


def dict_from_django_context(context):
    dict_ = {}
    # Newest dicts are up front, so update from oldest to newest.
    for subcontext in reversed(list(context)):
        dict_.update(subcontext)
    return dict_


def render_to_response(template_name, dictionary=None, context_instance=None,
                       mimetype=None):
    """
    :param template_name: Filename of the template to get or a sequence of
        filenames to try, in order.
    :param dictionary: Rendering context for the template.
    :returns: A response object with the evaluated template as a payload.
    """
    template = _ENV.get_template(template_name)
    if isinstance(dictionary, DjangoContext):
        dictionary = dict_from_django_context(dictionary)
    assert isinstance(dictionary, dict) # Required for **-operator.
    if context_instance:
        dictionary.update(dict_from_django_context(context_instance))
    rendered = template.render(**dictionary)
    return HttpResponse(rendered, mimetype=mimetype)
