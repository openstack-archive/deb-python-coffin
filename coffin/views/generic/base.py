import django.views.generic.base as _generic_base
from coffin.template.response import TemplateResponse as JinjaTemplateResponse

class TemplateResponseMixin(_generic_base.TemplateResponseMixin):
    """
    A mixin that can be used to render a template using Jinja.
    """
    response_class = JinjaTemplateResponse

class TemplateView(TemplateResponseMixin, _generic_base.TemplateView):
    """
    A view that renders a template using Jinja.
    """