import os
import warnings

from django import dispatch
from jinja2 import Environment, loaders


__all__ = ('get_env', 'need_env')


_ENV = None
_LOADERS = [] # See :fun:`_infer_loaders`.
_TEMPLATE_LIBS = []
_JINJA_I18N_EXTENSION_NAME = 'jinja2.ext.i18n'


need_env = dispatch.Signal(providing_args=['arguments', 'loaders',
                                           'filters', 'extensions'])


def _get_loaders():
    """Tries to translate each template loader given in the Django settings
    (:mod:`django.settings`) to a similarly-behaving Jinja loader.
    Warns if a similar loader cannot be found.
    Allows for Jinja2 loader instances to be placed in the template loader
    settings.
    """
    from coffin.template.loaders import jinja_loader_from_django_loader
    if _LOADERS:
        return _LOADERS
    from django.conf import settings
    for loader in settings.TEMPLATE_LOADERS:
        if isinstance(loader, basestring):
            loader_obj = jinja_loader_from_django_loader(loader)
            if loader_obj:
                _LOADERS.append(loader_obj)
            else:
                warnings.warn('Cannot translate loader: %s' % loader)
        else: # It's assumed to be a Jinja2 loader instance.
            _LOADERS.append(loader)
    return _LOADERS


def _get_templatelibs():
    """Return an iterable of template ``Library`` instances.

    Since we cannot support the {% load %} tag in Jinja, we have to
    register all libraries globally.
    """
    if _TEMPLATE_LIBS:
        return _TEMPLATE_LIBS

    from django.conf import settings
    from django.template import get_library, InvalidTemplateLibrary

    for a in settings.INSTALLED_APPS:
        try:
            path = __import__(a + '.templatetags', {}, {}, ['']).__file__
            path = os.path.dirname(path)  # we now have the templatetags/ directory
        except ImportError:
            pass
        else:
            for f in os.listdir(path):
                if f == '__init__.py':
                    continue
                if f.endswith('.py'):
                    try:
                        # TODO: will need updating when #6587 lands
                        _TEMPLATE_LIBS.append(get_library(
                            "django.templatetags.%s" % os.path.splitext(f)[0]))
                    except InvalidTemplateLibrary:
                        pass
    return _TEMPLATE_LIBS


def _get_filters():
    """Returns a list of filters to provide through Jinja. This includes
    ported versions of Django's builtin filters that Jinja is lacking,
    as well as custom filters as specified by the user in the settings.

    :return: A mapping of names to filters.
    """
    from django.conf import settings
    from coffin.template import builtins

    filters = {}
    # start with our default builtins
    for lib in builtins:
        if hasattr(lib, 'jinja2_filters'):
            filters.update(lib.jinja2_filters)

    # add the globally defined filter list
    user = getattr(settings, 'JINJA2_FILTERS', {})
    from django.core.urlresolvers import get_callable
    if isinstance(user, dict):
        for key, value in user.items():
            filters[user] = callable(value) and value or get_callable(value)
    else:
        for value in user:
            value = callable(value) and value or get_callable(value)
            filters[value.__name__] = value

    # add filters defined in application's templatetag libraries
    for lib in _get_templatelibs():
        if hasattr(lib, 'jinja2_filters'):
            filters.update(lib.jinja2_filters)

    return filters


def _get_extensions():
    from django.conf import settings
    from coffin.template import builtins

    extensions = []
    # start with our default builtins
    for lib in builtins:
        if hasattr(lib, 'jinja2_extensions'):
            extensions += lib.jinja2_extensions

    if settings.USE_I18N:
        extensions.append(_JINJA_I18N_EXTENSION_NAME)

    # add the globally defined extension list
    extensions += list(getattr(settings, 'JINJA2_EXTENSIONS', []))

    # add extensions defined in application's templatetag libraries
    for lib in _get_templatelibs():
        if hasattr(lib, 'jinja2_extensions'):
            extensions += lib.jinja2_extensions

    return extensions


def get_env():
    """
    :return: A Jinja2 environment singleton.
    """
    global _ENV
    if not _ENV:
        loaders_ = _get_loaders()
        filters = _get_filters()
        extensions = _get_extensions()
        arguments = {
            'autoescape': True,
        }

        need_env.send(sender=Environment, arguments=arguments,
                      loaders=loaders_, extensions=extensions,
                      filters=filters)

        if not _ENV:
            if not 'loader' in arguments:
                arguments['loader'] = loaders.ChoiceLoader(loaders_)
            if not 'extensions' in arguments:
                arguments['extensions'] = extensions

            _ENV = Environment(**arguments)
            _ENV.filters.update(filters)
            from coffin.template import Template as CoffinTemplate
            _ENV.template_class = CoffinTemplate
    return _ENV