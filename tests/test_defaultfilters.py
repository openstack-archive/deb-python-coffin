from datetime import datetime, date
from nose.tools import assert_raises
from coffin.common import get_env

def r(s, context={}):
    return get_env().from_string(s).render(context)

def test_url():
    # project name is optional
    assert r('{{ "urls_app.views.index"|url() }}') == '/url_test/'
    assert r('{{ "apps.urls_app.views.index"|url() }}') == '/url_test/'


def test_pluralize():
    assert r('vote{{ 0|pluralize }}') == 'votes'
    assert r('vote{{ 1|pluralize }}') == 'vote'
    assert r('class{{ 2|pluralize("es") }}') == 'classes'
    assert r('cand{{ 0|pluralize("y", "ies") }}') == 'candies'
    assert r('cand{{ 1|pluralize("y", "ies") }}') == 'candy'
    assert r('cand{{ 2|pluralize("y", "ies") }}') == 'candies'
    assert r('vote{{ [1,2,3]|pluralize }}') == 'votes'
    assert_raises(TypeError, r, 'vote{{ x|pluralize }}', {'x': object()})
    assert_raises(ValueError, r, 'vote{{ x|pluralize }}', {'x': 'foo'})


def test_date_stuff():
    assert r('a{{ d|date("Y") }}b', {'d': date(2007, 01, 01)}) == 'a2007b'
    assert r('a{{ d|time("H") }}b', {'d': datetime(2007, 01, 01, 12, 01, 01)}) == 'a12b'
    # TODO: timesince, timeuntil

    # Make sure the date filters can handle unset values gracefully.
    # While generally we'd like to be explicit instead of hiding errors,
    # this is a particular case where it makes sense.
    for f in ('date', 'time', 'timesince', 'timeuntil'):
        assert r('a{{ d|%s }}b' % f) == 'ab'
        assert r('a{{ d|%s }}b' % f, {'d': None}) == 'ab'
        # given an empty string though (wrong type), an error would be raced
        assert_raises(Exception, get_env().from_string('a{{ d|%s }}b' % f).render, {'d': ''})