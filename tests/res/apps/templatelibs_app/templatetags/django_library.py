"""Register a filter with a Django library object.
"""

def foo(value):
    return "{foo}"

from django.template import Library
register = Library()
register.filter('foo_django', foo)