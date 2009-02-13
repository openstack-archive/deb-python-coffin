"""Tests for ``coffin.template``.

``coffin.template.library``, ``coffin.template.defaultfilters`` and
``coffin.template.defaulttags`` have their own test modules.
"""


def test_template_class():
    from coffin.template import Template
    from coffin.common import get_env

    # initializing a template directly uses Coffin's Jinja
    # environment - we know it does if our tags are available.
    t = Template('{% spaceless %}{{ ""|truncatewords }}{% endspaceless %}')
    assert t.environment == get_env()

    # render can accept a Django context object
    from django.template import Context
    c = Context()
    c.update({'x': '1'})  # update does a push
    c.update({'y': '2'})
    assert Template('{{x}};{{y}}').render(c) == '1;2'


#def test_render_to_string():
#    # [bug] Test that the values given directly do overwrite does that
    # are already exist in the given context_instance. Due to a bug this
#    # was previously not the case.
#    from django.template import Context
#    c = Context({'x': 'old'})
#    assert render_to_string)