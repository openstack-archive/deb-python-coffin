"""Register a Jinja2 global object with a Coffin library object.
"""

def hello_func(name):
    return u"Hello %s" % name

from coffin.template import Library
register = Library()
register.object('hello', hello_func)
