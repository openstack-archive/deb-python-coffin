# coding=utf-8
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from coffin.common import env


def get_flatpages(starts_with=None, user=None, site_id=None):
    """
    Context-function similar to get_flatpages tag in Django templates.

    Usage:
        <ul>
            {% for page in get_flatpages(starts_with='/about/', user=user, site_id=site.pk) %}
                <li><a href="{{ page.url }}">{{ page.title }}</a></li>
            {% endfor %}
        </ul>

    """
    flatpages = FlatPage.objects.filter(sites__id=site_id or settings.SITE_ID)

    if starts_with:
        flatpages = flatpages.filter(url__startswith=starts_with)

    if not user or not user.is_authenticated():
        flatpages = flatpages.filter(registration_required=False)

    return flatpages

env.globals['get_flatpages'] = get_flatpages
