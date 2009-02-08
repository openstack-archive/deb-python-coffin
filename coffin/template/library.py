"""
General notes:

  - The Django ``stringfilter`` decorator is supported, but should not be
    used when writing filters specifically for Jinja: It will lose the
    attributes attached to the filter function by Jinja's
    ``environmentfilter`` and ``contextfilter`` decorators, when used
    in the wrong order.

    Maybe coffin should provide a custom version of stringfilter.

  - Rather than the global JINJA2_EXTENSIONS and JINJA2_FILTERS settings,
    coffin could try to register Django's "builtins". One could then use
    ``add_to_builtins`` to provide global components and avoid using
    {% load %}.

  - While transparently converting filters between Django and Jinja works
    for the most part, there is an issue with Django's
    ``mark_for_escaping``, as Jinja does not support a similar mechanism.
    Instead, for Jinja, we escape such strings immediately (whereas Django
    defers it to the template engine).
"""

import inspect
from django.template import Library as DjangoLibrary, InvalidTemplateLibrary
from django.utils.safestring import SafeUnicode, SafeData, EscapeData
from jinja2 import Markup, environmentfilter
from jinja2.ext import Extension as Jinja2Extension


__all__ = ('Library',)


class Library(DjangoLibrary):
    """Version of the Django ``Library`` class that can handle both
    Django template engine tags and filters, as well as Jinja2
    extensions and filters.

    Tries to present a common registration interface to the extension
    author, but provides both template engines with only those
    components they can support.

    Since custom Django tags and Jinja2 extensions are two completely
    different beasts, they are handled completely separately. You can
    register custom Django tags as usual, for example:

        register.tag('current_time', do_current_time)

    Or register a Jinja2 extension like this:

        register.tag(CurrentTimeNode)

    Filters, on the other hand, work similarily in both engines, and
    for the most one can't tell whether a filter function was written
    for Django or Jinja2. A compatibility layer is used to make to
    make the filters you register usuable with both engines:

        register.filter('cut', cut)

    However, some of the more powerful filters just won't work in
    Django, for example if more than one argument is required, or if
    context- or environmentfilters are used. If ``cut`` in the above
    example where such an extended filter, it would only be registered
    with Jinja.

    TODO: Jinja versions of the ``simple_tag`` and ``inclusion_tag``
    helpers would be nice, though since custom tags are not needed as
    often in Jinja, this is not urgent.
    """

    def __init__(self):
        super(Library, self).__init__()
        self.jinja2_filters = {}
        self.jinja2_extensions = []

    @classmethod
    def from_django(cls, django_library):
        """Create a Coffin library object from a Django library.

        Specifically, this ensures that filters already registered
        with the Django library are also made available to Jinja,
        where applicable.
        """
        from copy import copy
        result = cls()
        result.filters = copy(django_library.filters)
        result.tags = copy(django_library.tags)
        for name, func in result.filters.iteritems():
            result._register_filter(name, func, jinja2_only=True)
        return result

    def tag(self, name_or_node=None, compile_function=None):
        """Register a Django template tag (1) or Jinja 2 extension (2).

        For (1), supports the same invocation syntax as the original
        Django version, including use as a decorator.

        For (2), since Jinja 2 extensions are classes (which can't be
        decorated), and have the tag name effectively built in, only the
        following syntax is supported:

            register.tag(MyJinjaExtensionNode)
        """
        if isinstance(name_or_node, Jinja2Extension):
            if compile_function:
                raise InvalidTemplateLibrary('"compile_function" argument not supported for Jinja2 extensions')
            self.jinja2_extensions.append(name_or_node)
            return name_or_node
        else:
            return super(Library, self).tag(name_or_node, compile_function)

    def tag_function(self, func_or_node):
        if issubclass(func_or_node, Jinja2Extension):
            self.jinja2_extensions.append(func_or_node)
            return func_or_node
        else:
            return super(Library, self).tag_function(func_or_node)

    def filter(self, name=None, filter_func=None, jinja2_only=False):
        """Register a filter with both the Django and Jinja2 template
        engines, if possible (or only Jinja2, if ``jinja2_only`` is
        specified).

        Implements a compatibility layer to handle the different
        auto-escaping approaches transparently. Extended Jinja2 filter
        features like environment- and contextfilters are however not
        supported in Django. Such filters will only be registered with
        Jinja.

        Supports the same invocation syntax as the original Django
        version, including use as a decorator.
        """
        def filter_function(f):
            return self._register_filter(
                getattr(f, "_decorated_function", f).__name__,
                f, jinja2_only=jinja2_only)
        if name == None and filter_func == None:
            # @register.filter()
            return filter_function
        elif filter_func == None:
            if (callable(name)):
                # @register.filter
                return self.filter_function(name)
            else:
                # @register.filter('somename') or @register.filter(name='somename')
                def dec(func):
                    return self.filter(name, func, jinja2_only=jinja2_only)
                return dec
        elif name != None and filter_func != None:
            # register.filter('somename', somefunc)
            return self._register_filter(name, filter_func,
                jinja2_only=jinja2_only)
        else:
            raise InvalidTemplateLibrary("Unsupported arguments to "
                "Library.filter: (%r, %r)", (name, filter_func))

    def _register_filter(self, name, func, jinja2_only=None):
        # with those attributes, we know we have a jinja filter we
        # cannot port to Django
        if hasattr(func, 'contextfilter') or \
           hasattr(func, 'environmentfilter'):
            self.jinja2_filters[name] = func
            return func

        # if there are more than two mandatory arguments, we know we
        # have a jinja filter that is not supported by Django
        args = inspect.getargspec(func)
        if len(args[0]) - (len(args[3]) if args[3] else 0) > 2:
            self.jinja2_filters[name] = func
            return func

        # Jinja supports a similar machanism to Django's
        # ``needs_autoescape`` filters (environment filters). We can
        # thus support Django filters that use it in Jinja with just
        # a little bit of parameter rewriting.
        if not hasattr(func, 'needs_autoescape'):
            django_func = jinja2_to_django_interop(func)
            jinja2_func = django_to_jinja2_interop(func)
        else:
            django_func = func     # we know now it was written for Django
            @environmentfilter
            def jinja2_func(environment, *args, **kwargs):
                kwargs['autoescape'] = environment.autoescape
                return django_to_jinja2_interop(func)(*args, **kwargs)
        # TODO: Django's "func.is_safe" is not yet handled

        # register with all engines
        if not jinja2_only:
            self.filters[name] = django_func
        self.jinja2_filters[name] = jinja2_func

        return (django_func, jinja2_func)


def django_to_jinja2_interop(filter_func):
    def _convert(v):
        if isinstance(v, SafeData):
            return Markup(v)
        if isinstance(v, EscapeData):
            return Markup.escape(v)       # not 100% equivalent, see mod docs
        return v
    def wrapped(*args, **kwargs):
        result = filter_func(*args, **kwargs)
        return _convert(result)
    return wrapped

def jinja2_to_django_interop(filter_func):
    def _convert(v):
        # TODO: for now, this is not even necessary: Markup strings have
        # a custom replace() method that is immume to Django's escape()
        # attempts.
        #if isinstance(v, Markup):
        #    return SafeUnicode(v)         # jinja is always unicode
        # ... Jinja does not have an EscapeData equivalent
        return v
    def wrapped(value, *args, **kwargs):
        result = filter_func(value, *args, **kwargs)
        return _convert(result)
    return wrapped
