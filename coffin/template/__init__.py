from itertools import chain
from django.template import (
    Context as DjangoContext,
    add_to_builtins as django_add_to_builtins,
    get_library)
from jinja2 import Template as _Jinja2Template, Markup
from coffin.common import get_env
from coffin.interop import django_safestring_to_jinja2_markup

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

        return get_env().from_string(template_string, template_class=cls)

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
            context = SafeStringCompatWrapper.wrap(context)
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


class SafeStringCompatWrapper(object):
    """Wraps around a given object and ensures that whenever a
    Django-type safe string is exposed by this object, it's methods, or
    (recursively) any subobjects, it is converted for
    Jinja2-compatibility.

    We are trying to insert this proxy as transparently as possible.
    First, we have to recognize that there are two possible ways
    data might be accessed from the wrapped object:

        * Via the item-protocol, i.e. ``proxy['foo']``
        * Via the attribute-protocol., i.e. ``proxy.foo``

    Therefore, the proxy implements __getattribute__, __getitem__, ...
    and ensures that any value returned is once again wrapped.

    The wrapped object may also be called, and thus we implement
    __call__, which will ensure that the result value is once again
    wrapped.

    Finally, the template engine may evaluate the object in order to
    write it to the output as a string. This is done by calling
    __unicode__. Now ordinarily, this case could be handled by the
    __call__ intercept: An object's ``__unicode__`` method would be
    transparently wrapped by this proxy, and it could be used and called
    as if the proxy weren't here.
    Unfortunately, there is a complication:

    It is common in Django for the __unicode__ method to return a safe
    string (which subsequently would be converted into a Jinja2 ``Markup``
    string by this proxy). However, while the Django template engine
    handles safe strings returned by __unicode__ just fine, Jinja2
    does not - it will simply ignore the markup and consider it to be
    just another string that needs to be escaped (*). Instead, Jinja2
    uses the ``__html__`` method.

    We solve this dilemma by intercepting attribute queries about
    ``__html__`` - Jinja2 (in it's escape function) first checks if this
    attribute exists, and if so, expects it to return a safe string.
    Now if the proxy wraps an object that has it's own __html__ method,
    that method will be used. Otherwise, the proxy provides a fake
    __html__ method that will then simple fall back to __unicode__.
    If the latter returns the safe string that __html__ requires, we're
    good. Otherwise, we manually escape it.


    TODO: Support for Django ticket #7261 would not only eliminate the
    need for the __html__ hack, but would essentially free us from having
    to do any SafeData/Markup conversion at all.

    TODO: An alternative approach to this proxy would be monkeypatching
    __html__ methods in the right places (e.g. Django Forms). If we were
    to patch Django's SafeData classes as well, we could generally avoid
    any conversion between the safe string types, i.e. like we're
    currently doing for filter compatibility. Normal operation of Django's
    template engine should not be effected, since the ``__html__``
    protocol is not used (yet - #7261). The downside is that it obviously
    only works for the things we patched, e.g. third party libraries that
    also do not support __html__ would still not work. We could provide
    tools to easily add the required patches to such 3rd party code,
    though.

    TODO: Right now, SafeStringCompatWrapper(1)+SafeStringCompatWrapper(2)
    is not possible; to restore this kind of functionality we would need
    to proxy slightly less agressively, for example, wrapping only
    user-defined types and callables (functions, methods, lambdas, ..),
    and leaving builtin types like int, str etc. alone (to an extend, we
    are already doing this).


    (*) Actually, it works fine if the speedups module is not compiled
        and the Python version of the escape() function is used. The
        escape() funktion checks whether it is given a Markup string
        (actually, if there is an __html__ method), and only escapes
        if that is not the case.

        However, the Python version, if passed a non-Markup string it
        1) is converted to unicode (__unicode__) is called, 2) is wrapped
        in a Markup() call and 3) escaped. Because the Markup() constructer
        in 2) checks once again for a __html__ method, a Markup-string
        returned by __unicode__ in 1) is handled correctly.

        The C-version of escape() however, if passed a non-Markup string,
        first 1) converts to unicode, 2) escapes the string and 3) wraps
        it in a Markup instance. Because 2) and 3) are exchanged here,
        the string will always be escaped in step 2), even if it is a safe
        string.


    Adapted from:
        http://code.activestate.com/recipes/496741/
    """

    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    @classmethod
    def wrap(cls, something):
        if something is None:
            return None

        something = django_safestring_to_jinja2_markup(something)
        if isinstance(something, Markup):
            return something
        elif type(something) in (str, unicode,):
            return something
        elif isinstance(something, cls):
            return something
        elif type(something) == dict:
            # handle only actual dicts as an optimization, subclasses
            # are wrapped fully so that e.g. additional methods are
            # handled properly as well.
            result = something.copy()
            for key in result:
                result[key] = cls.wrap(result[key])
            return result
        else:
            return cls(something)

    def _html_helper(self):
        result = unicode(self)
        if isinstance(result, Markup):
            return result
        else:
            return Markup.escape(result)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        try:
            return SafeStringCompatWrapper.wrap(getattr(object.__getattribute__(self, "_obj"), name))
        except AttributeError:
            if name == '__html__':
                # return our fake html method
                return object.__getattribute__(self, "_html_helper")
            else:
                raise


    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)
    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj"), name, value)
    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))
    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))
    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__',  '__index__',
        '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]
    _special_names_wrapped = [
        '__call__', '__getitem__', '__getslice__',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        def make_method(name, wrapped):
            def method(self, *args, **kw):
                result = getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)
                if wrapped:
                    return cls.wrap(result)
                else:
                    return result

            return method

        namespace = {}
        for proplist, wrap in ((cls._special_names, False), (cls._special_names_wrapped, True)):
            for name in proplist:
                if hasattr(theclass, name):
                    namespace[name] = make_method(name, wrap)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins


# libraries to load by default for a new environment
builtins = []


def add_to_builtins(module_name):
    """Add the given module to both Coffin's list of default template
    libraries as well as Django's. This makes sense, since Coffin
    libs are compatible with Django libraries.

    You can still use Django's own ``add_to_builtins`` to register
    directly with Django and bypass Coffin.

    TODO: Allow passing path to (or reference of) extensions and
    filters directly. This would make it easier to use this function
    with 3rd party Jinja extensions that do not know about Coffin and
    thus will not provide a Library object.

    XXX/TODO: Why do we need our own custom list of builtins? Our
    Library object is compatible, remember!? We can just add them
    directly to Django's own list of builtins.
    """
    builtins.append(get_library(module_name))
    django_add_to_builtins(module_name)


add_to_builtins('coffin.template.defaulttags')
add_to_builtins('coffin.template.defaultfilters')