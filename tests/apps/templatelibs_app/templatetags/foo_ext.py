"""Register a Jinja2 extension with a Coffin library object.
"""

from jinja2.ext import Extension
from jinja2 import nodes

class FooExtension(Extension):
    tags = set(['foo'])

    def parse(self, parser):
        parser.stream.next()
        return nodes.Const('{foo}')

from coffin.template import Library
register = Library()
register.tag(FooExtension)