import warnings

from jinja2 import Environment, loaders

from coffin.template.loaders import jinja_loader_from_django_loader


__all__ = ('get_env', 'dict_from_django_context')


_ENV = None
_LOADERS = [] # See :fun:`_infer_loaders`.


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
    """Provides universally used filters; i.e. the `url` function
    that ties into Django's URLConf.

    :return: A mapping of names to filters.
    """
    def url(view_name, *args, **kwargs):
        from django.core.urlresolvers import reverse, NoReverseMatch
        url = reverse(view_name, args=args, kwargs=kwargs)
        return url
    return locals()


def get_env():
    """
    :return: A Jinja2 environment singleton.
    """
    global _ENV
    if not _ENV:
        loaders_ = _get_loaders()
        _ENV = Environment(loader=loaders.ChoiceLoader(loaders_))
        _ENV.filters.update(_get_filters())
    return _ENV


def dict_from_django_context(context):
    """Flattens a Django :class:`django.template.context.Context` object."""
    dict_ = {}
    # Newest dicts are up front, so update from oldest to newest.
    for subcontext in reversed(list(context)):
        dict_.update(subcontext)
    return dict_
