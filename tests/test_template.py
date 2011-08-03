"""Tests for ``coffin.template``.

``coffin.template.library``, ``coffin.template.defaultfilters`` and
``coffin.template.defaulttags`` have their own test modules.
"""

def test_template_class():
    from coffin.template import Template
    from coffin.common import env

    # initializing a template directly uses Coffin's Jinja
    # environment - we know it does if our tags are available.
    t = Template('{% spaceless %}{{ ""|truncatewords }}{% endspaceless %}')
    assert t.environment == env

    # render can accept a Django context object
    from django.template import Context
    c = Context()
    c.update({'x': '1'})  # update does a push
    c.update({'y': '2'})
    assert Template('{{x}};{{y}}').render(c) == '1;2'

    # [bug] render can handle nested Context objects
    c1 = Context(); c2 = Context(); c3 = Context()
    c3['foo'] = 'bar'
    c2.update(c3)
    c1.update(c2)
    assert Template('{{foo}}').render(c1) == 'bar'

    # There is a "origin" attribute for Django compatibility
    assert Template('{{foo}}').origin.name == '<template>'


def test_render_to_string():
    # [bug] Test that the values given directly do overwrite does that
    # are already exist in the given context_instance. Due to a bug this
    # was previously not the case.
    from django.template import Context
    from coffin.template.loader import render_to_string
    assert render_to_string('render-x.html', {'x': 'new'},
        context_instance=Context({'x': 'old'})) == 'new'

    # [bug] Test that the values from context_instance actually make it
    # into the template.
    assert render_to_string('render-x.html',
        context_instance=Context({'x': 'foo'})) == 'foo'

    # [bug] Call without the optional ``context_instance`` argument works
    assert render_to_string('render-x.html', {'x': 'foo'}) == 'foo'

    # ``dictionary`` argument may be a Context instance
    assert render_to_string('render-x.html', Context({'x': 'foo'})) == 'foo'

    # [bug] Both ``dictionary`` and ``context_instance`` may be
    # Context objects
    assert render_to_string('render-x.html', Context({'x': 'foo'}), context_instance=Context()) == 'foo'