#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(name='Coffin',
    version=".".join(map(str, __import__("coffin").__version__)),
    description='Jinja2 adapter for Django',
    author='Christopher D. Leary',
    author_email='cdleary@gmail.com',
    maintainer='David Cramer',
    maintainer_email='dcramer@gmail.com',
    url='http://github.com/coffin/coffin',
    packages=find_packages(),
    #install_requires=['Jinja2', 'django>=1.2'],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
