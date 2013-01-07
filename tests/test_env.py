"""Test construction of the implicitly provided JinjaEnvironment,
in the common.py module.
"""

from coffin.common import get_env
from django.test.utils import override_settings


def test_i18n():
    with override_settings(USE_I18N=True):
        assert get_env().from_string('{{ _("test") }}').render() == 'test'


class TestLoaders:

    def test_django_loader_replace(self):
        from coffin.template.loaders import jinja_loader_from_django_loader
        from jinja2 import loaders

        # Test replacement of filesystem loader
        l = jinja_loader_from_django_loader('django.template.loaders.filesystem.Loader')
        assert isinstance(l, loaders.FileSystemLoader)

        # Since we don't do exact matches for the loader string, make sure we
        # are not replacing loaders that are outside the Django namespace.
        l = jinja_loader_from_django_loader('djangoaddon.template.loaders.filesystem.Loader')
        assert not isinstance(l, loaders.FileSystemLoader)

    def test_cached_loader(self):
        from jinja2 import loaders

        with override_settings(TEMPLATE_LOADERS=[
            ('django.template.loaders.cached.Loader', (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )),]):
            env = get_env()
            assert len(env.loader.loaders) == 1
            cached_loader = get_env().loader.loaders[0]
            assert hasattr(cached_loader, 'template_cache')
            assert len(cached_loader.loader.loaders) == 2
            assert isinstance(cached_loader.loader.loaders[0], loaders.FileSystemLoader)

            # the cached loader can find a template too.
            assert env.loader.load(env, 'render-x.html').render({'x': 'foo'}) == 'foo'

