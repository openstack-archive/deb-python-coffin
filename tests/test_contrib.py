from coffin.template import add_to_builtins as add_to_coffin_builtins
from django.template import add_to_builtins as add_to_django_builtins
from coffin.common import get_env
from django.template import Template, Context


def test_markup():
    add_to_coffin_builtins('coffin.contrib.markup.templatetags.markup')
    add_to_django_builtins('coffin.contrib.markup.templatetags.markup')

    # Make sure filters will be available in both Django and Coffin.
    # Note that we do not assert the result - if markdown is not installed,
    # the filter will just return the input text. We don't care, we simple
    # want to check the filter is available.
    get_env().from_string('{{ "**Title**"|markdown }}').render()  # '\n<p><strong>Title</strong>\n</p>\n\n\n'
    Template('{{ "**Title**"|markdown }}').render(Context())