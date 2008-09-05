from django.template import TemplateDoesNotExist
from jinja2.exceptions import TemplateNotFound as JinjaTemplateNotFound

from coffin import _ENV


__all__ = (
    'render_to_string',
    'get_template',
    'get_template_from_string',
    'render_to_string',
)


def find_template_source(name, dirs=None):
    """
    Tries template loaders sequentially until one can find a template with the
    appropriate name.

    :returns: A (source, origin) tuple.
    """
    raise NotImplementedError


def get_template(template_name):
    """Delegates to :meth:`jinja2.Environment.get_template`.
    :raises django.template.TemplateDoesNotExist: If the template cannot be
        located. See :meth:`jinja2.loaders.BaseLoader.get_source` for exception
        conditions.
    :returns: A template object for the given template name.
    """
    try:
        return _ENV.get_template(template_name)
    except JinjaTemplateNotFound:
        raise TemplateDoesNotExist(template_name)


def render_to_string(template_name, dictionary=None, context_instance=None):
    """
    :param template_name: Filename of the template to get.
    :param dictionary: Rendering context for the template.
    :returns: Rendered template in the context of dictionary.
    """
    dict_ = dictionary or {}
    if isinstance(template_name, (list, tuple)):
        t = select_template(template_name)
    else:
        t = get_template(template_name)
    raise NotImplementedError('Update context instance with dict_.')


def get_template_from_string(template_name, origin=None, name=None):
    raise NotImplementedError('What to do with origin and name?')


def select_template(template_name_list):
    for template_name in template_name_list:
        try:
            return get_template(template_name)
        except:
            raise NotImplementedError('Handle unknown exception.')
    raise NotImplementedError('No templates could be loaded.')
