"""Register a Django tag with a Coffin library object.
"""

from django.template import Node

class FooNode(Node):
    def render(self, context):
        return u'{foo}'

def do_foo(parser, token):
    return FooNode()

from coffin.template import Library
register = Library()
register.tag('foo_coffin', do_foo)