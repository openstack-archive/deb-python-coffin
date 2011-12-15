from django.views.generic.base import RedirectView, TemplateView as _TemplateView
from coffin.views.decorators import template_response

__all__ = ['RedirectView', 'TemplateView']

TemplateView = template_response(_TemplateView)
