from coffin.template import loader
from django.views.generic import list_detail as _list_detail
import functools

object_list = functools.partial(_list_detail.object_list, template_loader=loader)
object_detail = functools.partial(_list_detail.object_detail, template_loader=loader)
