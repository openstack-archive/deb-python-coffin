from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from django.conf import settings


class LoadExtension(Extension):
    """The load-tag is a no-op in Coffin. Instead, all template libraries
    are always loaded.

    Note: Supporting a functioning load-tag in Jinja is tough, though
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


class URLExtension(Extension):
    """Returns an absolute URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% url path.to.some_view arg1,arg2,name1=value1 %}

    Known differences to Django's url-Tag:

        - In Django, the view name may contain any non-space character.
          Since Jinja's lexer does not identify whitespace to us, only
          characters that make up valid identifers, plus dots and hyphens
          are allowed. Note that identifers in Jinja 2 may not contain
          non-ascii characters.

          As an alternative, you may specifify the view as a string,
          which bypasses all these restrictions. It further allows you
          to apply filters:

            {% url "меткаda.some-view"|afilter %}
    """

    tags = set(['url'])

    def parse(self, parser):
        stream = parser.stream

        tag = stream.next()

        # get view name
        if stream.current.test('string'):
            viewname = parser.parse_primary()
        else:
            # parse valid tokens and manually build a string from them
            bits = []
            name_allowed = True
            while True:
                if stream.current.test_any('dot', 'sub'):
                    bits.append(stream.next())
                    name_allowed = True
                elif stream.current.test('name') and name_allowed:
                    bits.append(stream.next())
                    name_allowed = False
                else:
                    break
            viewname = nodes.Const("".join([b.value for b in bits]))
            if not bits:
                raise TemplateSyntaxError("'%s' requires path to view" % tag.value,
                                          tag.lineno)

        # get arguments
        args = []
        kwargs = []
        while not stream.current.test_any('block_end', 'name:as'):
            if args or kwargs:
                stream.expect('comma')
            if stream.current.test('name') and stream.look().test('assign'):
                key = nodes.Const(stream.next().value)
                stream.skip()
                value = parser.parse_expression()
                kwargs.append(nodes.Pair(key, value, lineno=key.lineno))
            else:
                args.append(parser.parse_expression())

        make_call_node = lambda *kw: \
            self.call_method('_reverse',
                             args=[viewname, nodes.List(args), nodes.Dict(kwargs)],
                             kwargs=kw)

        # if an as-clause is specified, write the result to context...
        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            call_node = make_call_node(nodes.Keyword('fail', nodes.Const(False)))
            return nodes.Assign(var, call_node)
        # ...otherwise print it out.
        else:
            return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

    @classmethod
    def _reverse(self, viewname, args, kwargs, fail=True):
        from django.core.urlresolvers import reverse, NoReverseMatch

        # Try to look up the URL twice: once given the view name,
        # and again relative to what we guess is the "main" app.
        url = ''
        try:
            url = reverse(viewname, args=args, kwargs=kwargs)
        except NoReverseMatch:
            projectname = settings.SETTINGS_MODULE.split('.')[0]
            try:
                url = reverse(projectname + '.' + viewname,
                              args=args, kwargs=kwargs)
            except NoReverseMatch:
                if fail:
                    raise
                else:
                    return ''

        return url


# nicer import names
load = LoadExtension
url = URLExtension