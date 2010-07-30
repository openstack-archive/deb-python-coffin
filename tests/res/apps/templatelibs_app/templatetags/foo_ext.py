"""Register a Jinja2 extension with a Coffin library object.
"""

from jinja2.ext import Extension
from jinja2 import nodes

class FooExtension(Extension):
    tags = set(['foo'])

    def parse(self, parser):
        parser.stream.next()
        return nodes.Const('{foo}')


class FooWithConfigExtension(Extension):
    tags = set(['foo_ex'])

    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.extend(
            foo_custom_output='foo',
        )

    def parse(self, parser):
        parser.stream.next()
        return nodes.Const('{%s}' % self.environment.foo_custom_output)


from coffin.template import Library
register = Library()
register.tag(FooExtension)
register.tag(FooWithConfigExtension, environment={'foo_custom_output': 'my_foo'})