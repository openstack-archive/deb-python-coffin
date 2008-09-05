"""
    coffin
    ~~~~~~

    coffin is a package that does its best to resolve the impedance mismatch
    between Django and Jinja2 through various adapters. The aim is to use
    Djinja2 as a drop-in replacement as possible for Django's template system
    to whatever extent is reasonable.

    :copyright: 2008 by Christopher D. Leary
    :license: BSD, see LICENSE for more details.
"""

__docformat__ = 'restructuredtext en'


from jinja2 import Environment, PackageLoader


_ENV = Environment()
