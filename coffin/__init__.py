"""
Coffin
~~~~~~

`Coffin <https://launchpad.net/coffin/>` is a package that resolves the
impedance mismatch between `Django <http://www.djangoproject.com/>` and `Jinja2
<http://jinja.pocoo.org/2/>` through various adapters. The aim is to use Coffin
as a drop-in replacement for Django's template system to whatever extent is
reasonable.

:copyright: 2008 by Christopher D. Leary
:license: BSD, see LICENSE for more details.
"""


__all__ = ('__version__', '__docformat__', 'get_revision')
__version__ = (0, 1)
__docformat__ = 'restructuredtext en'


import os


def _get_bzr_revision(bzr_dir):
    revision_file = os.path.join(bzr_dir, 'branch', 'last-revision')
    if not os.path.exists(revision_file):
        return None
    fh = open(revision_file, 'r')
    try:
        revno = fh.read().split(None, 1)[0] # Assumes file starts with revno.
        return int(revno)
    finally:
        fh.close()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, '..'))
    bzr_dir = os.path.join(checkout_dir, '.bzr')
    if os.path.exists(bzr_dir):
        return _get_bzr_revision(bzr_dir)
    return None
