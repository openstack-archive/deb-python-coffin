from nose.plugins.skip import SkipTest
import django


class TestSyndication:

    def test_old(self):
        from django.http import HttpRequest
        fake_request = HttpRequest()
        fake_request.META['SERVER_NAME'] = 'foo'
        fake_request.META['SERVER_PORT'] = 80

        from apps.feeds_app.feeds import TestOldFeed
        feedgen = TestOldFeed('', fake_request).get_feed(None)
        s = feedgen.writeString('utf-8')
        assert 'JINJA WAS HERE (TITLE)' in s
        assert 'JINJA WAS HERE (DESCRIPTION)' in s

    def test_new(self):
        if django.VERSION < (1,2):
            raise SkipTest()

        from django.http import HttpRequest
        fake_request = HttpRequest()
        fake_request.META['SERVER_NAME'] = 'foo'
        fake_request.META['SERVER_PORT'] = 80

        from apps.feeds_app.feeds import TestNewFeed
        response = TestNewFeed()(fake_request)
        assert 'JINJA WAS HERE (TITLE)' in response.content
        assert 'JINJA WAS HERE (DESCRIPTION)' in response.content