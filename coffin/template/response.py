from coffin.template import loader
from django.template import response as django_response


class SimpleTemplateResponse(django_response.SimpleTemplateResponse):
    def resolve_template(self, template):
        if isinstance(template, (list, tuple)):
            return loader.select_template(template)
        elif isinstance(template, basestring):
            return loader.get_template(template)
        else:
            return template

class TemplateResponse(django_response.TemplateResponse,
        SimpleTemplateResponse):
    pass
