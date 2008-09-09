from distutils.core import setup

import coffin

setup(
    name='Coffin',
    version=coffin.__version__,
    description='Jinja2 adapter for Django',
    author='Christopher D. Leary',
    author_email='cdleary@gmail.com',
    url='https://launchpad.net/coffin',
    packages=['coffin', 'coffin.shortcuts', 'coffin.template'],
)
