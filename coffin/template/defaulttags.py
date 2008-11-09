from jinja2 import nodes
from jinja2.ext import Extension


class LoadExtension(Extension):
    """The load-tag is a no-op in Jinja2. Instead, all template libraries
    are always loaded.

    Note: Supporting a functioning load-tag in Jinja is though, though
    theoretically possible. The trouble is activating new extensions while
    parsing is ongoing. The ``Parser.extensions`` dict of the current
    parser instance needs to be modified, but apparently the only way to
    get access would be by hacking the stack.
    """

    tags = set(['load'])

    def parse(self, parser):
        while not parser.stream.current.type == 'block_end':
            parser.stream.next()

        return nodes.Const('')