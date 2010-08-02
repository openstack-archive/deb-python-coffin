"""Register a number of portable filters (with a Coffin library object)
that require a compatibility layer to function correctly in both engines.
"""

from jinja2 import Markup
from django.utils.safestring import mark_safe, mark_for_escaping


def needing_autoescape(value, autoescape=None):
    return str(autoescape)
needing_autoescape.needs_autoescape = True


def jinja_safe_output(value):
    return Markup(value)

def django_safe_output(value):
    return mark_safe(value)

def unsafe_output(value):
    return unicode(value)


def django_raw_output(value):
    return value

def django_escape_output(value):
    # Make sure the value is converted to unicode first, because otherwise,
    # if it is already SafeData (for example, when coming from the template
    # code), then mark_for_escaping would do nothing. We want to guarantee
    # a EscapeData return value in this filter though.
    return mark_for_escaping(unicode(value))


from coffin.template import Library
register = Library()
register.filter('needing_autoescape', needing_autoescape)
register.filter('jinja_safe_output', jinja_safe_output)
register.filter('django_safe_output', django_safe_output)
register.filter('django_raw_output', django_raw_output)
register.filter('unsafe_output', unsafe_output)
register.filter('django_escape_output', django_escape_output)