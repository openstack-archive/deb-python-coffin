from django.contrib.syndication.feeds import *       # merge modules

import sys
from django.contrib.syndication.feeds import Feed as DjangoDeprecatedFeed
from django.contrib.syndication.views import Feed as DjangoNewFeed
from coffin.template import loader as coffin_loader
from django import VERSION as DJANGO_VERSION


class Feed(DjangoDeprecatedFeed):
    """Django changed the syndication framework in 1.2. This class
    represents the old way, ported to Coffin. If you are using 1.2,
    you should use the ``Feed`` class in
    ``coffin.contrib.syndication.views``.

    See also there for some notes on what we are doing here.
    """

    def get_feed(self, *args, **kwargs):
        if DJANGO_VERSION < (1,2):
            parent_module = sys.modules[DjangoDeprecatedFeed.__module__]
        else:
            # In Django 1.2, our parent DjangoDeprecatedFeed class really
            # inherits from DjangoNewFeed, so we need to patch the loader
            # in a different module.
            parent_module = sys.modules[DjangoNewFeed.__module__]

        old_loader = parent_module.loader
        parent_module.loader = coffin_loader
        try:
            return super(Feed, self).get_feed(*args, **kwargs)
        finally:
            parent_module.loader = old_loader