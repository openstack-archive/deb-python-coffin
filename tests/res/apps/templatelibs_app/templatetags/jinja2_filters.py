"""Register a number of non-portable, Jinja2-only filters with a Coffin
library object.
"""

from jinja2 import environmentfilter, contextfilter

@environmentfilter
def environment(environment, value):
    return ""

@contextfilter
def context(context, value):
    return ""

def multiarg(value, arg1, arg2):
    return ""

def jinja_forced(value):
    return ""

def django_jinja_forced(value):
    # a django filter that returns a django-safestring. It will *only*
    # be added to jinja, and coffin will hopefully ensure the string
    # stays safe.
    from django.utils.safestring import mark_safe
    return mark_safe(value)


from coffin.template import Library
register = Library()
register.filter('environment', environment)
register.filter('context', context)
register.filter('multiarg', multiarg)
register.filter('jinja_forced', jinja_forced, jinja2_only=True)
register.filter('django_jinja_forced', django_jinja_forced, jinja2_only=True)