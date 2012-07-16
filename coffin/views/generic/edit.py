from coffin.views.generic.base import TemplateResponseMixin
from coffin.views.generic.detail import SingleObjectTemplateResponseMixin
import django.views.generic.edit as _generic_edit


class FormView(TemplateResponseMixin, _generic_edit.BaseFormView):
    """
    Equivalent of django generic view FormView, but uses Jinja template renderer.
    """


class CreateView(SingleObjectTemplateResponseMixin, _generic_edit.BaseCreateView):
    """
    Equivalent of django generic view CreateView, but uses Jinja template renderer.
    """
    template_name_suffix = '_form'


class UpdateView(SingleObjectTemplateResponseMixin, _generic_edit.BaseUpdateView):
    """
    Equivalent of django generic view UpdateView, but uses Jinja template renderer.
    """
    template_name_suffix = '_form'


class DeleteView(SingleObjectTemplateResponseMixin, _generic_edit.BaseDeleteView):
    """
    Equivalent of django generic view DeleteView, but uses Jinja template renderer.
    """
    template_name_suffix = '_confirm_delete'
