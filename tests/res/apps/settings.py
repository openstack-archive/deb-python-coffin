from os import path


DATABASES = {
    'default': {}
}

INSTALLED_APPS = (
    'templatelibs_app',
    'feeds_app',
    'urls_app',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
)

TEMPLATE_DIRS = (path.join(path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'