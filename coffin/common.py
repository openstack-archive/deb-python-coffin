import os
import warnings

from django import dispatch
from jinja2 import Environment, loaders
from jinja2 import defaults as jinja2_defaults
from coffin.template import Library as CoffinLibrary

__all__ = ('env',)

env = None

_JINJA_I18N_EXTENSION_NAME = 'jinja2.ext.i18n'

class CoffinEnvironment(Environment):
    def __init__(self, filters={}, globals={}, tests={}, loader=None, extensions=[], **kwargs):
        if not loader:
            loader = loaders.ChoiceLoader(self._get_loaders())
        all_ext = self._get_all_extensions()

        extensions.extend(all_ext['extensions'])
        super(CoffinEnvironment, self).__init__(
            extensions=extensions,
            loader=loader,
            **kwargs
        )
        # Note: all_ext already includes Jinja2's own builtins (with
        # the proper priority), so we want to assign to these attributes.
        self.filters = all_ext['filters'].copy()
        self.filters.update(filters)
        self.globals.update(all_ext['globals'])
        self.globals.update(globals)
        self.tests = all_ext['tests'].copy()
        self.tests.update(tests)
        for key, value in all_ext['attrs'].items():
            setattr(self, key, value)

        from coffin.template import Template as CoffinTemplate
        self.template_class = CoffinTemplate

    def _get_loaders(self):
        """Tries to translate each template loader given in the Django settings
        (:mod:`django.settings`) to a similarly-behaving Jinja loader.
        Warns if a similar loader cannot be found.
        Allows for Jinja2 loader instances to be placed in the template loader
        settings.
        """
        loaders = []

        from coffin.template.loaders import jinja_loader_from_django_loader
        from jinja2.loaders import BaseLoader as JinjaLoader

        from django.conf import settings
        _loaders = getattr(settings, 'JINJA2_TEMPLATE_LOADERS', settings.TEMPLATE_LOADERS)
        for loader in _loaders:
            if isinstance(loader, JinjaLoader):
                loaders.append(loader)
            else:
                loader_name = args = None
                if isinstance(loader, basestring):
                    loader_name = loader
                    args = []
                elif isinstance(loader, (tuple, list)):
                    loader_name = loader[0]
                    args = loader[1]

                if loader_name:
                    loader_obj = jinja_loader_from_django_loader(loader_name, args)
                    if loader_obj:
                        loaders.append(loader_obj)
                        continue

                warnings.warn('Cannot translate loader: %s' % loader)
        return loaders

    def _get_templatelibs(self):
        """Return an iterable of template ``Library`` instances.

        Since we cannot support the {% load %} tag in Jinja, we have to
        register all libraries globally.
        """
        from django.conf import settings
        from django.template import (
            get_library, import_library, InvalidTemplateLibrary)

        libs = []
        for app in settings.INSTALLED_APPS:
            ns = app + '.templatetags'
            try:
                path = __import__(ns, {}, {}, ['__file__']).__file__
                path = os.path.dirname(path)  # we now have the templatetags/ directory
            except ImportError:
                pass
            else:
                for filename in os.listdir(path):
                    if filename == '__init__.py' or filename.startswith('.'):
                        continue

                    if filename.endswith('.py'):
                        try:
                            module = "%s.%s" % (ns, os.path.splitext(filename)[0])
                            l = import_library(module)
                            libs.append(l)

                        except InvalidTemplateLibrary:
                            pass

        # In addition to loading application libraries, support a custom list
        for libname in getattr(settings, 'JINJA2_DJANGO_TEMPLATETAG_LIBRARIES', ()):
            libs.append(get_library(libname))

        return libs

    def _get_all_extensions(self):
        from django.conf import settings
        from django.template import builtins as django_builtins
        from coffin.template import builtins as coffin_builtins
        from django.core.urlresolvers import get_callable

        # Note that for extensions, the order in which we load the libraries
        # is not maintained (https://github.com/mitsuhiko/jinja2/issues#issue/3).
        # Extensions support priorities, which should be used instead.
        extensions, filters, globals, tests, attrs = [], {}, {}, {}, {}
        def _load_lib(lib):
            if not isinstance(lib, CoffinLibrary):
                # If this is only a standard Django library,
                # convert it. This will ensure that Django
                # filters in that library are converted and
                # made available in Jinja.
                lib = CoffinLibrary.from_django(lib)
            extensions.extend(getattr(lib, 'jinja2_extensions', []))
            filters.update(getattr(lib, 'jinja2_filters', {}))
            globals.update(getattr(lib, 'jinja2_globals', {}))
            tests.update(getattr(lib, 'jinja2_tests', {}))
            attrs.update(getattr(lib, 'jinja2_environment_attrs', {}))

        # Start with Django's builtins; this give's us all of Django's
        # filters courtasy of our interop layer.
        for lib in django_builtins:
            _load_lib(lib)

        # The stuff Jinja2 comes with by default should override Django.
        filters.update(jinja2_defaults.DEFAULT_FILTERS)
        tests.update(jinja2_defaults.DEFAULT_TESTS)
        globals.update(jinja2_defaults.DEFAULT_NAMESPACE)

        # Our own set of builtins are next, overwriting Jinja2's.
        for lib in coffin_builtins:
            _load_lib(lib)

        # Optionally, include the i18n extension.
        if settings.USE_I18N:
            extensions.append(_JINJA_I18N_EXTENSION_NAME)

        # Next, add the globally defined extensions
        extensions.extend(list(getattr(settings, 'JINJA2_EXTENSIONS', [])))
        def from_setting(setting, values_must_be_callable = False):
            retval = {}
            setting = getattr(settings, setting, {})
            if isinstance(setting, dict):
                for key, value in setting.iteritems():
                    if values_must_be_callable and not callable(value):
                        value = get_callable(value)
                    retval[key] = value
            else:
                for value in setting:
                    if values_must_be_callable and not callable(value):
                        value = get_callable(value)
                    retval[value.__name__] = value
            return retval

        tests.update(from_setting('JINJA2_TESTS', True))
        filters.update(from_setting('JINJA2_FILTERS', True))
        globals.update(from_setting('JINJA2_GLOBALS'))

        # Finally, add extensions defined in application's templatetag libraries
        for lib in self._get_templatelibs():
            _load_lib(lib)

        return dict(
            extensions=extensions,
            filters=filters,
            globals=globals,
            tests=tests,
            attrs=attrs,
        )

def get_env():
    """
    :return: A Jinja2 environment singleton.
    """
    from django.conf import settings

    kwargs = {
        'autoescape': True,
    }
    kwargs.update(getattr(settings, 'JINJA2_ENVIRONMENT_OPTIONS', {}))

    result = CoffinEnvironment(**kwargs)
    # Hook Jinja's i18n extension up to Django's translation backend
    # if i18n is enabled; note that we differ here from Django, in that
    # Django always has it's i18n functionality available (that is, if
    # enabled in a template via {% load %}), but uses a null backend if
    # the USE_I18N setting is disabled. Jinja2 provides something similar
    # (install_null_translations), but instead we are currently not
    # enabling the extension at all when USE_I18N=False.
    # While this is basically an incompatibility with Django, currently
    # the i18n tags work completely differently anyway, so for now, I
    # don't think it matters.
    if settings.USE_I18N:
        from django.utils import translation
        result.install_gettext_translations(translation)

    return result

env = get_env()
