from coffin.template.response import TemplateResponse

def template_response(cls):
    """
    A decorator to enforce class_based generic views 
    to use coffin TemplateResponse
    """
    cls.response_class = TemplateResponse
    return cls
