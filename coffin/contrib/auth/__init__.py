_modules = (
    'models',
    'fixtures',
    'handlers',
    'management',
    'tests',
    'admin',
    'backends',
    'create_superuser',
    'decorators',
    'forms',
    'middleware',
    'tokens',
)
for m in _modules:
    globals()[m] = __import__('django.contrib.auth', globals(), locals(), [m], -1)