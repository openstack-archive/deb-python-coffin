"""Test the various features of our custom library object.
"""

from nose.tools import assert_raises

from jinja2 import TemplateAssertionError as Jinja2TemplateAssertionError
from django.template import Template, Context, \
    TemplateSyntaxError as DjangoTemplateSyntaxError


# TODO: It would be preferrable to split these tests into those checks
# which actually test the Library object, and those which test the assembly
# of the Environment instance. Testcode for the former could be written more
# cleanly by creating the library instances within the test code and
# registering them manually with the environment, rather than having to
# place them in fake Django apps in completely different files to have
# them loaded.
# The tests for the compatibility layer could also be factored out.


def test_nodes_and_extensions():
    """Test availability of registered nodes/extensions.
    """
    from coffin.common import env

    # Jinja2 extensions, loaded from a Coffin library
    assert env.from_string('a{% foo %}b').render() == 'a{foo}b'
    assert env.from_string('a{% foo_ex %}b').render() == 'a{my_foo}b'

    # Django tags, loaded from a Coffin library
    assert Template('{% load django_tags %}a{% foo_coffin %}b').render(Context()) == 'a{foo}b'


def test_objects():
    """For coffin, global objects can be registered.
    """
    from coffin.common import env

    # Jinja2 global objects, loaded from a Coffin library
    assert env.from_string('{{ hello("John") }}').render() == 'Hello John'


def test_filters():
    """Test availability of registered filters.
    """
    from coffin.common import env

    # Filter registered with a Coffin library is available in Django and Jinja2
    assert env.from_string('a{{ "b"|foo }}c').render() == 'a{foo}c'
    assert Template('{% load portable_filters %}a{{ "b"|foo }}c').render(Context()) == 'a{foo}c'

    # Filter registered with a Django library is also available in Jinja2
    Template('{% load django_library %}{{ "b"|foo_django }}').render(Context())
    assert env.from_string('a{{ "b"|foo }}c').render() == 'a{foo}c'

    # Some filters, while registered with a Coffin library, are only
    # available in Jinja2:
    # - when using @environmentfilter
    env.from_string('{{ "b"|environment }}')
    assert_raises(Exception, Template, '{% load jinja2_filters %}{{ "b"|environment }}')
    # - when using @contextfilter
    env.from_string('{{ "b"|context }}')
    assert_raises(Exception, Template, '{% load jinja2_filters %}{{ "b"|context }}')
    # - when requiring more than one argument
    env.from_string('{{ "b"|multiarg(1,2) }}')
    assert_raises(Exception, Template, '{% load jinja2_filters %}{{ "b"|multiarg }}')
    # - when Jinja2-exclusivity is explicitly requested
    env.from_string('{{ "b"|jinja_forced }}')
    assert_raises(Exception, Template, '{% load jinja2_filters %}{{ "b"|jinja_forced }}')
    # [bug] Jinja2-exclusivity caused the compatibility layer to be not
    # applied, causing for example safe strings to be escaped.
    assert env.from_string('{{ "><"|django_jinja_forced }}').render() == '><'


def test_env_builtins_django():
    """Test that when the environment is assembled, Django libraries which
    are included in the list of builtins are properly supported.
    """
    from coffin.common import get_env
    from coffin.template import add_to_builtins
    add_to_builtins('apps.django_lib')
    assert get_env().from_string('a{{ "b"|foo_django_builtin }}c').render() == 'a{foo}c'


def test_filter_compat_safestrings():
    """Test filter compatibility layer with respect to safe strings.
    """
    from coffin.common import env
    env.autoescape = True

    # Jinja-style safe output strings are considered "safe" by both engines
    assert env.from_string('{{ "<b>"|jinja_safe_output }}').render() == '<b>'
    # TODO: The below actually works regardless of our converting between
    # the same string types: Jinja's Markup() strings are actually immune
    # to Django's escape() attempt, since they have a custom version of
    # replace() that operates on an already escaped version.
    assert Template('{% load compat_filters %}{{ "<b>"|jinja_safe_output }}').render(Context()) == '<b>'

    # Unsafe, unmarked output strings are considered "unsafe" by both engines
    assert env.from_string('{{ "<b>"|unsafe_output }}').render() == '&lt;b&gt;'
    assert Template('{% load compat_filters %}{{ "<b>"|unsafe_output }}').render(Context()) == '&lt;b&gt;'

    # Django-style safe output strings are considered "safe" by both engines
    assert env.from_string('{{ "<b>"|django_safe_output }}').render() == '<b>'
    assert Template('{% load compat_filters %}{{ "<b>"|django_safe_output }}').render(Context()) == '<b>'


def test_filter_compat_escapetrings():
    """Test filter compatibility layer with respect to strings flagged as
    "wanted for escaping".
    """
    from coffin.common import env
    env.autoescape = False

    # Django-style "force escaping" works in both engines
    assert env.from_string('{{ "<b>"|django_escape_output }}').render() == '&lt;b&gt;'
    assert Template('{% load compat_filters %}{{ "<b>"|django_escape_output }}').render(Context()) == '&lt;b&gt;'


def test_filter_compat_other():
    """Test other features of the filter compatibility layer.
    """
    # A Django filter with @needs_autoescape works in Jinja2
    from coffin.common import env
    env.autoescape = True
    assert env.from_string('{{ "b"|needing_autoescape }}').render() == 'True'
    env.autoescape = False
    assert env.from_string('{{ "b"|needing_autoescape }}').render() == 'False'

    # [bug] @needs_autoescape also (still) works correctly in Django
    assert Template('{% load compat_filters %}{{ "b"|needing_autoescape }}').render(Context()) == 'True'

    # The Django filters can handle "Undefined" values
    assert env.from_string('{{ doesnotexist|django_raw_output }}').render() == ''

    # TODO: test @stringfilter
