INSTALLED_APPS = (
    'templatelibs_app',
    'feeds_app',
    'urls_app',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

ROOT_URLCONF = 'urls'