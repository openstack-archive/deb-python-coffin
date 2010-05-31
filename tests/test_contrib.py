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