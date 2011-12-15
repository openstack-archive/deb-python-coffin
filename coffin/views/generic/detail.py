from django.views.generic.detail import DetailView as _DetailView
from coffin.views.decorators import template_response

__all__ = ['DetailView']

DetailView = template_response(_DetailView)
