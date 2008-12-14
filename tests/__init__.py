from os import path
import sys

def setup_package():
    # setup Django with our test demo project
    sys.path.insert(0, path.join(path.dirname(__file__), 'res', 'apps'))
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
