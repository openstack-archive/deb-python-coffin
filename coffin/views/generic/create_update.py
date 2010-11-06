from coffin.template import loader
from django.views.generic import create_update as _create_update
import functools

create_object = functools.partial(_create_update.create_object, template_loader=loader)
update_object = functools.partial(_create_update.update_object, template_loader=loader)
delete_object = functools.partial(_create_update.delete_object, template_loader=loader)
