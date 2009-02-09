from datetime import datetime, date
from nose.tools import assert_raises
from coffin.common import get_env

def test_url():
    env = get_env()
    # project name is optional
    assert env.from_string('{{ "urls_app.views.index"|url() }}').render() == '/url_test/'
    assert env.from_string('{{ "apps.urls_app.views.index"|url() }}').render() == '/url_test/'


def test_date_stuff():
    env = get_env()

    assert env.from_string('a{{ d|date("Y") }}b').render({'d': date(2007, 01, 01)}) == 'a2007b'
    assert env.from_string('a{{ d|time("H") }}b').render({'d': datetime(2007, 01, 01, 12, 01, 01)}) == 'a12b'
    # TODO: timesince, timeuntil

    # Make sure the date filters can handle unset values gracefully.
    # While generally we'd like to be explicit instead of hiding errors,
    # this is a particular case where it makes sense.
    for f in ('date', 'time', 'timesince', 'timeuntil'):
        assert env.from_string('a{{ d|%s }}b' % f).render() == 'ab'
        assert env.from_string('a{{ d|%s }}b' % f).render({'d': None}) == 'ab'
        # given an empty string though (wrong type), an error would be raced
        assert_raises(Exception, env.from_string('a{{ d|%s }}b' % f).render, {'d': ''})