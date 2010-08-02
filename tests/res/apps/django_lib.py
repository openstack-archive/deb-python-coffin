"""A Django library, but but auto-loaded via the templatetags/ directory.

Instead, to use it, it needs to be added to the builtins.
"""

def foo(value):
    return "{foo}"

from django.template import Library
register = Library()
register.filter('foo_django_builtin', foo)
