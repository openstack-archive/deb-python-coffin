try:
    from urllib.parse import urljoin
except ImportError:     # Python 2
    from urlparse import urljoin

from jinja2.ext import Extension
from jinja2 import nodes
from django.utils.encoding import iri_to_uri


class PrefixExtension(Extension):

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno

        call_node = self.call_method('render')

        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            return nodes.Assign(var, call_node).set_lineno(lineno)
        else:
            return nodes.Output([call_node]).set_lineno(lineno)

    def render(self, name):
        raise NotImplementedError()

    @classmethod
    def get_uri_setting(cls, name):
        try:
            from django.conf import settings
        except ImportError:
            prefix = ''
        else:
            prefix = iri_to_uri(getattr(settings, name, ''))
        return prefix


class GetStaticPrefixExtension(PrefixExtension):
    """
    Populates a template variable with the static prefix,
    ``settings.STATIC_URL``.

    Usage::

        {% get_static_prefix [as varname] %}

    Examples::

        {% get_static_prefix %}
        {% get_static_prefix as static_prefix %}

    """

    tags = set(['get_static_prefix'])

    def render(self):
        return self.get_uri_setting('STATIC_URL')


class GetMediaPrefixExtension(PrefixExtension):
    """
    Populates a template variable with the media prefix,
    ``settings.MEDIA_URL``.

    Usage::

        {% get_media_prefix [as varname] %}

    Examples::

        {% get_media_prefix %}
        {% get_media_prefix as media_prefix %}

    """

    tags = set(['get_media_prefix'])

    def render(self):
        return self.get_uri_setting('STATIC_URL')


class StaticExtension(PrefixExtension):
    """
    Joins the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}

    """

    tags = set(['static'])

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno

        path = parser.parse_expression()
        call_node = self.call_method('get_statc_url', args=[path])

        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            return nodes.Assign(var, call_node).set_lineno(lineno)
        else:
            return nodes.Output([call_node]).set_lineno(lineno)

    @classmethod
    def get_statc_url(cls, path):
        return urljoin(PrefixExtension.get_uri_setting("STATIC_URL"), path)
