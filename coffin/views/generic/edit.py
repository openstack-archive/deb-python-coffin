from django.views.generic.edit import CreateView as _CreateView, UpdateView as _UpdateView, DeleteView as _DeleteView
from coffin.views.decorators import template_response

__all__ = ['CreateView', 'UpdateView', 'DeleteView']

CreateView, UpdateView, DeleteView = map(template_response,
        (_CreateView, _UpdateView, _DeleteView)) 

