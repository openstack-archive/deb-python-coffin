from django.template import (
    Context as DjangoContext,
    add_to_builtins as django_add_to_builtins,
    import_library)
from jinja2 import Template as _Jinja2Template

# Merge with ``django.template``.
from django.template import __all__
from django.template import *

# Override default library class with ours
from library import *


class Template(_Jinja2Template):
    """Fixes the incompabilites between Jinja2's template class and
    Django's.

    The end result should be a class that renders Jinja2 templates but
    is compatible with the interface specfied by Django.

    This includes flattening a ``Context`` instance passed to render
    and making sure that this class will automatically use the global
    coffin environment.
    """

    def __new__(cls, template_string, origin=None, name=None):
        # We accept the "origin" and "name" arguments, but discard them
        # right away - Jinja's Template class (apparently) stores no
        # equivalent information.
        from coffin.common import env

        return env.from_string(template_string, template_class=cls)

    def __iter__(self):
        # TODO: Django allows iterating over the templates nodes. Should
        # be parse ourself and iterate over the AST?
        raise NotImplementedError()

    def render(self, context=None):
        """Differs from Django's own render() slightly in that makes the
        ``context`` parameter optional. We try to strike a middle ground
        here between implementing Django's interface while still supporting
        Jinja's own call syntax as well.
        """
        if context is None:
            context = {}
        else:
            context = dict_from_django_context(context)
        assert isinstance(context, dict)  # Required for **-operator.
        return super(Template, self).render(**context)


def dict_from_django_context(context):
    """Flattens a Django :class:`django.template.context.Context` object.
    """
    if not isinstance(context, DjangoContext):
        return context
    else:
        dict_ = {}
        # Newest dicts are up front, so update from oldest to newest.
        for subcontext in reversed(list(context)):
            dict_.update(dict_from_django_context(subcontext))
        return dict_


# Make available the ports of Django tags and filters that Coffin provides.
from django.template import add_to_builtins
add_to_builtins('coffin.template.defaulttags')
add_to_builtins('coffin.template.defaultfilters')