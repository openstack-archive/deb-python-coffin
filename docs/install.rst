Installation
============

Install the package through PyPi::

    easy_install Coffin

Or alternatively, get the source::

    git clone git://github.com/dcramer/coffin.git
    cd coffin
    python setup.py install

Once installed, you will need to add Coffin to several places throughout your projects.

First, open up ``settings.py`` and add Coffin to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'coffin',
        ...
    )

The easiest way to enable Jinja2, rather than Django, is to change your import paths. For example, if we're using the ``render_to_response`` shortcut, we simply need to tweak our import line::

    from django.shortcuts import render_to_response

To the following::

    from coffin.shortcuts import render_to_response

Coffin includes drop in replacements for the following Django modules:

* :mod:`django.shortcuts`
* :mod:`django.views.generic.simple`
* :mod:`django.contrib.auth`
* :mod:`django.contrib.markup`
* :mod:`django.contrib.syndication`
* :mod:`django.template`