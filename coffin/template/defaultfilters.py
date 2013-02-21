"""Coffin automatically makes Django's builtin filters available in Jinja2,
through an interop-layer.

However, Jinja 2 provides room to improve the syntax of some of the
filters. Those can be overridden here.

TODO: Most of the filters in here need to be updated for autoescaping.
"""

from coffin.template import Library
from jinja2.runtime import Undefined
# from jinja2 import Markup
from jinja2 import filters

register = Library()

def url(view_name, *args, **kwargs):
    """This is an alternative to the {% url %} tag. It comes from a time
    before Coffin had a port of the tag.
    """
    from coffin.template.defaulttags import url
    return url._reverse(view_name, args, kwargs)
register.jinja2_filter(url, jinja2_only=True)
register.object(url)

@register.jinja2_filter(jinja2_only=True)
def timesince(value, *arg):
    if value is None or isinstance(value, Undefined):
        return u''
    from django.utils.timesince import timesince
    return timesince(value, *arg)

@register.jinja2_filter(jinja2_only=True)
def timeuntil(value, *args):
    if value is None or isinstance(value, Undefined):
        return u''
    from django.utils.timesince import timeuntil
    return timeuntil(value, *args)

@register.jinja2_filter(jinja2_only=True)
def date(value, arg=None):
    """Formats a date according to the given format."""
    if value is None or isinstance(value, Undefined):
        return u''
    from django.conf import settings
    from django.utils import formats
    from django.utils.dateformat import format
    if arg is None:
        arg = settings.DATE_FORMAT
    try: 
        return formats.date_format(value, arg) 
    except AttributeError:
        try: 
            return format(value, arg) 
        except AttributeError:
            return ''

@register.jinja2_filter(jinja2_only=True)
def time(value, arg=None):
    """Formats a time according to the given format."""
    if value is None or isinstance(value, Undefined):
        return u''
    from django.conf import settings
    from django.utils import formats
    from django.utils.dateformat import time_format
    if arg is None:
        arg = settings.TIME_FORMAT
    try: 
        return formats.time_format(value, arg) 
    except AttributeError:
        try: 
            return time_format(value, arg) 
        except AttributeError:
            return ''

@register.jinja2_filter(jinja2_only=True)
def truncatewords(value, length):
    # Jinja2 has it's own ``truncate`` filter that supports word
    # boundaries and more stuff, but cannot deal with HTML.
    from django.utils.text import truncate_words
    return truncate_words(value, int(length))

@register.jinja2_filter(jinja2_only=True)
def truncatewords_html(value, length):
    from django.utils.text import truncate_html_words
    return truncate_html_words(value, int(length))

@register.jinja2_filter(jinja2_only=True)
def pluralize(value, s1='s', s2=None):
    """Like Django's pluralize-filter, but instead of using an optional
    comma to separate singular and plural suffixes, it uses two distinct
    parameters.

    It also is less forgiving if applied to values that do not allow
    making a decision between singular and plural.
    """
    if s2 is not None:
        singular_suffix, plural_suffix = s1, s2
    else:
        plural_suffix = s1
        singular_suffix = ''

    try:
        if int(value) != 1:
            return plural_suffix
    except TypeError: # not a string or a number; maybe it's a list?
        if len(value) != 1:
            return plural_suffix
    return singular_suffix

@register.jinja2_filter(jinja2_only=True)
def floatformat(value, arg=-1):
    """Builds on top of Django's own version, but adds strict error
    checking, staying with the philosophy.
    """
    from django.template.defaultfilters import floatformat
    from coffin.interop import django_filter_to_jinja2
    arg = int(arg)  # raise exception
    result = django_filter_to_jinja2(floatformat)(value, arg)
    if result == '':  # django couldn't handle the value
        raise ValueError(value)
    return result

@register.jinja2_filter(jinja2_only=True)
def default(value, default_value=u'', boolean=True):
    """Make the default filter, if used without arguments, behave like
    Django's own version.
    """
    return filters.do_default(value, default_value, boolean)

