from coffin.common import env
from django.template import Template, Context


def test_markup():
    from coffin.template import add_to_builtins as add_to_coffin_builtins
    from django.template import add_to_builtins as add_to_django_builtins
    add_to_coffin_builtins('coffin.contrib.markup.templatetags.markup')
    add_to_django_builtins('coffin.contrib.markup.templatetags.markup')

    # Make sure filters will be available in both Django and Coffin.
    # Note that we do not assert the result - if markdown is not installed,
    # the filter will just return the input text. We don't care, we simple
    # want to check the filter is available.
    env.from_string('{{ "**Title**"|markdown }}').render()  # '\n<p><strong>Title</strong>\n</p>\n\n\n'
    Template('{{ "**Title**"|markdown }}').render(Context())


def test_syndication():
    from django.http import HttpRequest
    fake_request = HttpRequest()
    fake_request.META['SERVER_NAME'] = 'foo'
    fake_request.META['SERVER_PORT'] = 80

    from apps.feeds_app.feeds import TestFeed
    feedgen = TestFeed('', fake_request).get_feed(None)
    s = feedgen.writeString('utf-8')
    assert 'JINJA WAS HERE (TITLE)' in s
    assert 'JINJA WAS HERE (DESCRIPTION)' in s