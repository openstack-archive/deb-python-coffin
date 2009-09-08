import os
from setuptools import setup, find_packages

import coffin

setup(name='Coffin',
    version='.'.join(map(str, coffin.__version__)),
    description='Jinja2 adapter for Django',
    author='Christopher D. Leary',
    author_email='cdleary@gmail.com',
    maintainer='David Cramer',
    maintainer_email='dcramer@gmail.com',
    url='http://github.com/dcramer/coffin',
    packages=find_packages(),
    install_requires=['Jinja2', 'django>=1.0'],
)
