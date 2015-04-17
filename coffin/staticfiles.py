from django.contrib.staticfiles.storage import staticfiles_storage
from coffin.static import StaticExtension


class StaticExtension(StaticExtension):
    """Implements the {% static %} tag as provided by the ``staticfiles``
    contrib module.

    Rreturns the URL to a file using staticfiles' storage backend.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}

    """

    @classmethod
    def get_statc_url(cls, path):
        return super(StaticExtension, cls).get_statc_url(
            staticfiles_storage.url(path))
