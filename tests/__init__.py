from os import path
import sys

# Setup Django with our test demo project. We need to do this in global
# module code rather than setup_package(), because we want it to run
# before any module-wide imports in any of the test modules.
sys.path.insert(0, path.join(path.dirname(__file__), 'res', 'apps'))

import os
import django
from templatelibs_app import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.res.apps.settings")
django.setup()

