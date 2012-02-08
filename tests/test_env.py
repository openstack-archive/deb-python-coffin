"""Test construction of the implicitly provided JinjaEnvironment,
in the common.py module.
"""

from coffin.common import get_env
from django.test.utils import override_settings


def test_i18n():
    with override_settings(USE_I18N=True):
        assert get_env().from_string('{{ _("test") }}').render() == 'test'


def test_django_loader_replace():
    from coffin.template.loaders import jinja_loader_from_django_loader
    from jinja2 import loaders

    # Test replacement of filesystem loader
    l = jinja_loader_from_django_loader('django.template.loaders.filesystem.Loader')
    assert isinstance(l, loaders.FileSystemLoader)

    # Since we don't do exact matches for the loader string, make sure we
    # are not replacing loaders that are outside the Django namespace.
    l = jinja_loader_from_django_loader('djangoaddon.template.loaders.filesystem.Loader')
    assert not isinstance(l, loaders.FileSystemLoader)
