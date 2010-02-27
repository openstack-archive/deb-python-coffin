import os
import warnings

from django import dispatch
from jinja2 import Environment, loaders

__all__ = ('env',)

env = None

_JINJA_I18N_EXTENSION_NAME = 'jinja2.ext.i18n'

class CoffinEnvironment(Environment):
    def __init__(self, filters={}, globals={}, tests={}, loader=None, extensions=[], **kwargs):
        if not loader:
            loader = loaders.ChoiceLoader(self._get_loaders())
        all_ext = self._get_all_extensions()
        
        extensions.extend(all_ext['extensions'])
        super(CoffinEnvironment, self).__init__(extensions=extensions, loader=loader, **kwargs)
        self.filters.update(filters)
        self.filters.update(all_ext['filters'])
        self.globals.update(globals)
        self.globals.update(all_ext['globals'])
        self.tests.update(tests)
        self.tests.update(all_ext['tests'])

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

        from django.conf import settings
        for loader in settings.TEMPLATE_LOADERS:
            if isinstance(loader, basestring):
                loader_obj = jinja_loader_from_django_loader(loader)
                if loader_obj:
                    loaders.append(loader_obj)
                else:
                    warnings.warn('Cannot translate loader: %s' % loader)
            else: # It's assumed to be a Jinja2 loader instance.
                loaders.append(loader)
        return loaders


    def _get_templatelibs(self):
        """Return an iterable of template ``Library`` instances.

        Since we cannot support the {% load %} tag in Jinja, we have to
        register all libraries globally.
        """
        from django.conf import settings
        from django.template import get_library, InvalidTemplateLibrary

        libs = []
        for a in settings.INSTALLED_APPS:
            try:
                path = __import__(a + '.templatetags', {}, {}, ['__file__']).__file__
                path = os.path.dirname(path)  # we now have the templatetags/ directory
            except ImportError:
                pass
            else:
                for f in os.listdir(path):
                    if f == '__init__.py':
                        continue
                    if f.endswith('.py'):
                        try:
                            # TODO: will need updating when #6587 lands
                            # libs.append(get_library(
                            #     "django.templatetags.%s" % os.path.splitext(f)[0]))
                            libs.append(get_library(os.path.splitext(f)[0]))
                            
                        except InvalidTemplateLibrary:
                            pass
        return libs

    def _get_all_extensions(self):
        from django.conf import settings
        from coffin.template import builtins
        from django.core.urlresolvers import get_callable

        extensions, filters, globals, tests = [], {}, {}, {}

        # start with our builtins
        for lib in builtins:
            extensions.extend(getattr(lib, 'jinja2_extensions', []))
            filters.update(getattr(lib, 'jinja2_filters', {}))
            globals.update(getattr(lib, 'jinja2_globals', {}))
            tests.update(getattr(lib, 'jinja2_tests', {}))

        if settings.USE_I18N:
            extensions.append(_JINJA_I18N_EXTENSION_NAME)

        # add the globally defined extension list
        extensions.extend(list(getattr(settings, 'JINJA2_EXTENSIONS', [])))

        def from_setting(setting):
            retval = {}
            setting = getattr(settings, setting, {})
            if isinstance(setting, dict):
                for key, value in setting.iteritems():
                    retval[key] = callable(value) and value or get_callable(value)
            else:
                for value in setting:
                    value = callable(value) and value or get_callable(value)
                    retval[value.__name__] = value
            return retval

        filters.update(from_setting('JINJA2_FILTERS'))
        globals.update(from_setting('JINJA2_GLOBALS'))
        tests.update(from_setting('JINJA2_TESTS'))

        # add extensions defined in application's templatetag libraries
        for lib in self._get_templatelibs():
            extensions.extend(getattr(lib, 'jinja2_extensions', []))
            filters.update(getattr(lib, 'jinja2_filters', {}))
            globals.update(getattr(lib, 'jinja2_globals', {}))
            tests.update(getattr(lib, 'jinja2_tests', {}))

        return dict(
            extensions=extensions,
            filters=filters,
            globals=globals,
            tests=tests,
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
