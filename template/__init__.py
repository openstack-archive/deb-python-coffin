from jinja2 import Template as JinjaTemplate
from django.conf import settings

from coffin.template.context import (
    Context,
    RequestContext,
    ContextPopException,
)
from coffin import _ENV


__all__ = ('compile_string', 'Context', 'RequestContext', 'Template')
_STANDARD_PROCESSORS = None


def compile_string(template_string, origin):
    raise NotImplementedError




class Template(object):
    """An adapter for Jinja2 templates with a Django template interface."""

    def __init__(self, template_string, origin=None,
                 name='<Unknown Template>'):
        self._template = _ENV.from_string(template_string)
        self.name = name
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def render(self, context):
        return self._template.render(**context)
