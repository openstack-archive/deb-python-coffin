"""Test construction of the implicitly provided JinjaEnvironment,
in the common.py module.
"""

from coffin.common import get_env
from django.test.utils import override_settings


def test_i18n():
    with override_settings(USE_I18N=True):
        assert get_env().from_string('{{ _("test") }}').render() == 'test'
