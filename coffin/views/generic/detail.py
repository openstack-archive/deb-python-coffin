import django.views.generic.detail as _generic_detail
from coffin.views.generic.base import TemplateResponseMixin as JinjaTemplateResponseMixin

class SingleObjectTemplateResponseMixin(JinjaTemplateResponseMixin, _generic_detail.SingleObjectTemplateResponseMixin):
    """
    Equivalent of django mixin SingleObjectTemplateResponseMixin, but uses Jinja template renderer.
    """

class DetailView(SingleObjectTemplateResponseMixin, _generic_detail.BaseDetailView):
    """
    Equivalent of django generic view DetailView, but uses Jinja template renderer.
    """
