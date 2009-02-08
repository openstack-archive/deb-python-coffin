from django.template import (
    add_to_builtins as django_add_to_builtins,
    get_library)

# Merge with ``django.template``.
from django.template import __all__
from django.template import *

# Override default library class with ours
from library import *


# libraries to load by default for a new environment
builtins = []


def add_to_builtins(module_name):
    """Add the given module to both Coffin's list of default template
    libraries as well as Django's. This makes sense, since Coffin
    libs are compatible with Django libraries.

    You can still use Django's own ``add_to_builtins`` to register
    directly with Django and bypass Coffin.

    TODO: Allow passing path to (or reference of) extensions and
    filters directly. This would make it easier to use this function
    with 3rd party Jinja extensions that do not know about Coffin and
    thus will not provide a Library object.
    """
    builtins.append(get_library(module_name))
    django_add_to_builtins(module_name)


add_to_builtins('coffin.template.defaulttags')
add_to_builtins('coffin.template.defaultfilters')