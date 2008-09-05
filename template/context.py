"""
Django's :class:`django.template.context.Context` is simple enough to be
reused direct -- it's just a slightly fancy mapping that doesn't require as
many hash insertions.

Django's context processors (:mod:`django.core.context_processors`) take a
request and return a mapping to be merged into the context, and thus require no
adaptation.

The :class:`django.template.context.RequestContext` is a simple wrapper around
a context that makes calls to context processors.
"""

from django.template.context import (
    Context,
    RequestContext,
    get_standard_processors,
    ContextPopException,
)
