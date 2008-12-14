import os
from distutils.core import setup

import coffin

def find_packages(root):
    # so we don't depend on setuptools; from the Storm ORM setup.py
    packages = []
    for directory, subdirectories, files in os.walk(root):
        if '__init__.py' in files:
            packages.append(directory.replace(os.sep, '.'))
    return packages

setup(
    name='Coffin',
    version=coffin.__version__,
    description='Jinja2 adapter for Django',
    author='Christopher D. Leary',
    author_email='cdleary@gmail.com',
    url='https://launchpad.net/coffin',
    packages=find_packages('coffin'),
)
