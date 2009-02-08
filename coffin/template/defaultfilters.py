"""Jinja2-ports of many of Django's default filters.

TODO: Most of the filters in here need to be updated for autoescaping.
"""

from coffin.template import Library


register = Library()


@register.filter(jinja2_only=True)
def url(view_name, *args, **kwargs):
    from coffin.template.defaulttags import url
    return url._reverse(view_name, args, kwargs)


@register.filter(jinja2_only=True)
def timesince(value, arg=None):
    from django.utils.timesince import timesince
    if arg:
        return timesince(value, arg)
    return timesince(value)


@register.filter(jinja2_only=True)
def timeuntil(value, arg=None):
    from django.utils.timesince import timeuntil
    return timeuntil(date, arg)


@register.filter(jinja2_only=True)
def date(value, arg=None):
    from django.conf import settings
    from django.utils.dateformat import format
    if arg is None:
        arg = settings.DATE_FORMAT
    return format(value, arg)


@register.filter(jinja2_only=True)
def time(value, arg=None):
    from django.conf import settings
    from django.utils.dateformat import time_format
    if arg is None:
        arg = settings.TIME_FORMAT
    return time_format(value, arg)