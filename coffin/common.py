from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError
from jinja2 import Markup
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
        return []


"""class AutoescapeExtension(Extension):
    ""#"
    Template to output works in three phases in Jinja2: parsing,
    generation (compilation, AST-traversal), and rendering (execution).

    Unfortunatly, the environment ``autoescape`` option comes into effect
    during traversal, the part where we happen to have basically no control
    over as an extension. It determines whether output is wrapped in
    ``escape()`` calls.

    Solutions that could possibly work:

        * This extension could preprocess it's childnodes and wrap
          everything output related inside the appropriate
          ``Markup()`` or escape() call.

        * We could use the ``preprocess`` hook to insert the
          appropriate ``|safe`` and ``|escape`` filters on a
          string-basis. This is very unlikely to work well.

    There's also the issue of inheritance and just generally the nesting
    of autoescape-tags to consider.

    Other things of note:

        * We can access ``parser.environment``, but that would only
          affect the **parsing** of our child nodes.

        * In the commented-out code below we are trying to affect the
          autoescape setting during rendering. As noted, this could be
          necessary for rare border cases where custom extension use
          the autoescape attribute.

    Both the above things would break Environment thread-safety though!

    Overall, it's not looking to good for this extension.
    ""#"

    tags = ['autoescape']

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        old_autoescape = parser.environment.autoescape
        parser.environment.autoescape = True
        try:
            body = parser.parse_statements(
                ['name:endautoescape'], drop_needle=True)
        finally:
            parser.environment.autoescape = old_autoescape

        # Not sure yet if the code below is necessary - it changes
        # environment.autoescape during template rendering. If for example
        # a CallBlock function accesses ``environment.autoescape``, it
        # presumably is.
        # This also should use try-finally though, which Jinja's API
        # doesn't support either. We could fake that as well by using
        # InternalNames that output the necessary indentation and keywords,
        # but at this point it starts to get really messy.
        #
        # TODO: Actually, there's ``nodes.EnvironmentAttribute``.
        #ae_setting = object.__new__(nodes.InternalName)
        #nodes.Node.__init__(ae_setting, 'environment.autoescape',
            lineno=lineno)
        #temp = parser.free_identifier()
        #body.insert(0, nodes.Assign(temp, ae_setting))
        #body.insert(1, nodes.Assign(ae_setting, nodes.Const(True)))
        #body.insert(len(body), nodes.Assign(ae_setting, temp))
        return body
"""


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
            # Need to work around Jinja2 syntax here. Jinja by default acts
            # like Python and concats subsequent strings. In this case
            # though, we want {% url "app.views.post" "1" %} to be treated
            # as view + argument, while still supporting
            # {% url "app.views.post"|filter %}. Essentially, what we do is
            # rather than let ``parser.parse_primary()`` deal with a "string"
            # token, we do so ourselves, and let parse_expression() handle all
            # other cases.
            if stream.look().test('string'):
                token = stream.next()
                viewname = nodes.Const(token.value, lineno=token.lineno)
            else:
                viewname = parser.parse_expression()
        else:
            # parse valid tokens and manually build a string from them
            bits = []
            name_allowed = True
            while True:
                if stream.current.test_any('dot', 'sub', 'colon'):
                    bits.append(stream.next())
                    name_allowed = True
                elif stream.current.test('name') and name_allowed:
                    bits.append(stream.next())
                    name_allowed = False
                else:
                    break
            viewname = nodes.Const("".join([b.value for b in bits]))
            if not bits:
                raise TemplateSyntaxError("'%s' requires path to view" %
                    tag.value, tag.lineno)

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

        def make_call_node(*kw):
            return self.call_method('_reverse', args=[
                viewname,
                nodes.List(args),
                nodes.Dict(kwargs),
                nodes.Name('_current_app', 'load'),
            ], kwargs=kw)

        # if an as-clause is specified, write the result to context...
        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            call_node = make_call_node(nodes.Keyword('fail',
                nodes.Const(False)))
            return nodes.Assign(var, call_node)
        # ...otherwise print it out.
        else:
            return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

    @classmethod
    def _reverse(self, viewname, args, kwargs, current_app=None, fail=True):
        from django.core.urlresolvers import reverse, NoReverseMatch

        # Try to look up the URL twice: once given the view name,
        # and again relative to what we guess is the "main" app.
        url = ''
        urlconf=kwargs.pop('urlconf', None)
        try:
            url = reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs,
                current_app=current_app)
        except NoReverseMatch as ex:
            projectname = settings.SETTINGS_MODULE.split('.')[0]
            try:
                url = reverse(projectname + '.' + viewname, urlconf=urlconf, 
                              args=args, kwargs=kwargs)
            except NoReverseMatch:
                if fail:
                    raise ex
                else:
                    return ''

        return url


class WithExtension(Extension):
    """Adds a value to the context (inside this block) for caching and
    easy access, just like the Django-version does.

    For example::

        {% with person.some_sql_method as total %}
            {{ total }} object{{ total|pluralize }}
        {% endwith %}

    TODO: The new Scope node introduced in Jinja2 6334c1eade73 (the 2.2
    dev version) would help here, but we don't want to rely on that yet.
    See also:
        http://dev.pocoo.org/projects/jinja/browser/tests/test_ext.py
        http://dev.pocoo.org/projects/jinja/ticket/331
        http://dev.pocoo.org/projects/jinja/ticket/329
    """

    tags = set(['with'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        value = parser.parse_expression()
        parser.stream.expect('name:as')
        name = parser.stream.expect('name')
        body = parser.parse_statements(['name:endwith'], drop_needle=True)
        # Use a local variable instead of a macro argument to alias
        # the expression.  This allows us to nest "with" statements.
        body.insert(0, nodes.Assign(nodes.Name(name.value, 'store'), value))
        return nodes.CallBlock(
                self.call_method('_render_block'), [], [], body).\
                    set_lineno(lineno)

    def _render_block(self, caller=None):
        return caller()


class SpacelessExtension(Extension):
    """Removes whitespace between HTML tags, including tab and
    newline characters.

    Works exactly like Django's own tag.
    """

    tags = set(['spaceless'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endspaceless'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_spaces', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        from django.utils.html import strip_spaces_between_tags
        return strip_spaces_between_tags(caller().strip())

# nicer import names
load = LoadExtension
url = URLExtension
with_ = WithExtension
spaceless = SpacelessExtension


# # I wish adding extensions in this way was supported
# try:
#     from django_jinja import library
# except ImportError:
#     pass
# else:
#     library.tag(load)
#     library.tag(url)
#     library.tag(with_)
#     library.tag(spaceless)
