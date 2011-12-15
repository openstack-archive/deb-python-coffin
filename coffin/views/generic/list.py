from django.views.generic.list import ListView as _ListView
from coffin.views.decorators import template_response

__all__ = ['ListView']

ListView = template_response(_ListView)
