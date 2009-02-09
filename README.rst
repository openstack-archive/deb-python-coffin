= Coffin: Jinja2 adapter for Django =


== Supported Django template functionality ==

Coffin currently makes the following Django tags available in Jinja:

    - {% url %} - additionally, a ``"view"|url()`` filter is also
      available.

    - {% load %} - is actually a no-op in Coffin, since templatetag
      libraries are always loaded. See also "Custom Filters and extensions".

    - {% with %}

Django filters that are ported in Coffin: date, time, timesince, timeuntil,
truncatewords, truncatewords_html.

The template-related functionality of the following contrib modules has
been ported in Coffin: ``coffin.contrib.markup``.

== Rendering ==

Simply use the ``render_to_response`` replacement provided by coffin:

    from coffin.shortcuts import render_to_response
    render_to_response('template.html', {'var': 1})

This will render ``template.html`` using Jinja2, and returns a
``HttpResponse``.


== 404 and 500 handlers ==

To have your HTTP 404 and 500 template rendered using Jinja, replace the
line

    from django.conf.urls.defaults import *

in your ``urls.py`` (it should be there by default), with

    from coffin.conf.urls.defaults import *


== Custom filters and extensions ==

Coffin uses the same templatetag library approach as Django, meaning
your app has a ``templatetags`` directory, and each of it's modules
represents a "template library", providing new filters and tags.

A custom ``Library`` class in ``coffin.template.Library`` can be used
to register Jinja-specific components.

Coffin can automatically make your existing Django filters usable in
Jinja, but not your custom tags - you need to rewrite those as Jinja
extensions manually.

Example for a Jinja-enabled template library:

    from coffin import template
    register = template.Library()

    register.filter('plenk', plenk)   # Filter for both Django and Jinja
    register.tag('foo', do_foo)       # Django version of the tag
    register.tag(FooExtension)        # Jinja version of the tag


== Other things of note ==

``coffin.template.loader`` is a port of ``django.template.loader`` and
comes with a Jinja2-enabled version of ``get_template()``.

A Jinja2-enabled version of ``add_to_builtins`` can be found in the
``django.template`` namespace.


== Things not supported by Coffin ==

These is an incomplete list things that Coffin does not yet and possibly
never will, requiring manual changes on your part:

    * The ``slice`` filter works differently in Jinja2 and Django.
      Replace it with Jinja's slice syntax: ``x[0:1]``.


== Running the tests ==

Use the nose framework:

    http://somethingaboutorange.com/mrl/projects/nose/