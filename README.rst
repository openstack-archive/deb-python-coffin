========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/deb-python-coffin.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

Coffin: Jinja2 extensions for Django
------------------------------------

This used to be a full-featured standalone adapter. With Django adding
support for other template backends, it's approach didn't make sense
anymore. Please use ``django_jinja`` instead - you won't regret it:

https://github.com/niwinz/django-jinja

This module now is a lean collection of some Django tags that are
not included in django-jinja, namely:

- {% url %}
- {% spaceless %}
- {% with %}
- {% load %} (as a noop)
- {% get_media_prefix %}
- {% get_static_prefix %}
- {% static %} (in a base variant, and with django.contrib.staticfiles support)