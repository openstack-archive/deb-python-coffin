import django.views.generic.list as _generic_list
from coffin.views.generic.base import TemplateResponseMixin as JinjaTemplateResponseMixin

class MultipleObjectTemplateResponseMixin(JinjaTemplateResponseMixin, _generic_list.MultipleObjectTemplateResponseMixin):
    """
    Equivalent of django mixin MultipleObjectTemplateResponseMixin, but uses Jinja template renderer.
    """

class ListView(MultipleObjectTemplateResponseMixin, _generic_list.BaseListView):
    """
    Equivalent of django generic view ListView, but uses Jinja template renderer.
    """
