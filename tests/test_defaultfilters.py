from coffin.common import get_env

def test_url():
    env = get_env()
    from django.core.urlresolvers import reverse
    # project name is optional
    assert env.from_string('{{ "urls_app.views.index"|url() }}').render() == '/url_test/'
    assert env.from_string('{{ "apps.urls_app.views.index"|url() }}').render() == '/url_test/'