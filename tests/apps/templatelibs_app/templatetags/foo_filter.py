"""Register a portable filter with a Coffin library object.
"""

def foo(value):
    return "{foo}"

from coffin.template import Library
register = Library()
register.filter('foo', foo)