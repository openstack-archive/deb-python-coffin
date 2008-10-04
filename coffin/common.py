import warnings

from jinja2 import Environment, loaders

from coffin.template.loaders import jinja_loader_from_django_loader


__all__ = ('get_env', 'dict_from_django_context')


_ENV = None
_LOADERS = [] # See :fun:`_infer_loaders`.
_JINJA_I18N_EXTENSION_NAME = 'jinja2.ext.i18n'


def _get_loaders():
    """Tries to translate each template loader given in the Django settings
    (:mod:`django.settings`) to a similarly-behaving Jinja loader.
    Warns if a similar loader cannot be found.
    Allows for Jinja2 loader instances to be placed in the template loader
    settings.
    """
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


def _get_filters():
    """Provides universally used filters; e.g. the `url` function
    that ties into Django's URLConf.

    :return: A mapping of names to filters.

    # TODO: Most of those need to updated for autoescaping
    """
    def url(view_name, *args, **kwargs):
        from django.core.urlresolvers import reverse, NoReverseMatch
        url = reverse(view_name, args=args, kwargs=kwargs)
        return url

    def timesince(value, arg=None):
        from django.utils.timesince import timesince
        if arg:
            return timesince(value, arg)
        return timesince(value)

    def timeuntil(value, arg=None):
        from django.utils.timesince import timeuntil
        return timeuntil(date, arg)

    def date(value, arg=None):
        from django.conf import settings
        from django.utils.dateformat import format
        if arg is None:
            arg = settings.DATE_FORMAT
        return format(value, arg)

    def time(value, arg=None):
        from django.conf import settings
        from django.utils.dateformat import time_format
        if arg is None:
            arg = settings.TIME_FORMAT
        return time_format(value, arg)

    return locals()


def _get_extensions():
    extensions = []
    from django.conf import settings
    if settings.USE_I18N:
        extensions.append(_JINJA_I18N_EXTENSION_NAME)
    return extensions


def get_env():
    """
    :return: A Jinja2 environment singleton.
    """
    global _ENV
    if not _ENV:
        loaders_ = _get_loaders()
        _ENV = Environment(
            loader=loaders.ChoiceLoader(loaders_),
            extensions=_get_extensions()
        )
        _ENV.filters.update(_get_filters())
    return _ENV


def dict_from_django_context(context):
    """Flattens a Django :class:`django.template.context.Context` object."""
    dict_ = {}
    # Newest dicts are up front, so update from oldest to newest.
    for subcontext in reversed(list(context)):
        dict_.update(subcontext)
    return dict_
