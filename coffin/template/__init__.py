from jinja2 import (
    exceptions as _jinja2_exceptions,
    environment as _jinja2_environment,
)
from django.template import (
    Context as DjangoContext,
    add_to_builtins as django_add_to_builtins,
    import_library,
    TemplateSyntaxError as DjangoTemplateSyntaxError,
    loader as django_loader,
)

# Merge with ``django.template``.
from django.template import __all__
from django.template import *

# Override default library class with ours
from library import *


def _generate_django_exception(e, source=None):
    '''Generate a Django exception from a Jinja exception'''
    from django.views.debug import linebreak_iter
    import re

    if source:
        exception = DjangoTemplateSyntaxError(e.message)
        exception_dict = e.__dict__
        del exception_dict['source']

        # Fetch the entire template in a string
        template_string = source[0].reload()

        # Get the line number from the error message, if available
        match = re.match('.* at (\d+)$', e.message)

        start_index = 0
        stop_index = 0
        if match:
            # Convert the position found in the stacktrace to a position
            # the Django template debug system can use
            position = int(match.group(1)) + source[1][0] + 1

            for index in linebreak_iter(template_string):
                if index >= position:
                    stop_index = min(index, position + 3)
                    start_index = min(index, position - 2)
                    break
                start_index = index

        else:
            # So there wasn't a matching error message, in that case we
            # simply have to highlight the entire line instead of the specific
            # words
            ignore_lines = -1
            for i, index in enumerate(linebreak_iter(template_string)):
                if source[1][0] > index:
                    ignore_lines += 1

                if i - ignore_lines == e.lineno:
                    stop_index = index
                    break

                start_index = index

        # Convert the positions to a source that is compatible with the
        # Django template debugger
        source = source[0], (
            start_index,
            stop_index,
        )
    else:
        # No source available so we let Django fetch it for us
        lineno = e.lineno - 1
        template_string, source = django_loader.find_template_source(e.name)
        exception = DjangoTemplateSyntaxError(e.message)

        # Find the positions by the line number given in the exception
        start_index = 0
        for i in range(lineno):
            start_index = template_string.index('\n', start_index + 1)

        source = source, (
            start_index + 1,
            template_string.index('\n', start_index + 1) + 1,
        )

    # Set our custom source as source for the exception so the Django
    # template debugger can use it
    exception.source = source
    return exception


class Template(_jinja2_environment.Template):
    '''Fixes the incompabilites between Jinja2's template class and
    Django's.

    The end result should be a class that renders Jinja2 templates but
    is compatible with the interface specfied by Django.

    This includes flattening a ``Context`` instance passed to render
    and making sure that this class will automatically use the global
    coffin environment.
    '''

    def __new__(cls, template_string, origin=None, name=None, source=None):
        # We accept the "origin" and "name" arguments, but discard them
        # right away - Jinja's Template class (apparently) stores no
        # equivalent information.

        # source is expected to be a Django Template Loader source, it is not
        # required but helps to provide useful stacktraces when executing
        # Jinja code from Django templates
        from coffin.common import env

        try:
            template = env.from_string(template_string, template_class=cls)
            template.source = source
            return template
        except _jinja2_exceptions.TemplateSyntaxError, e:
            raise _generate_django_exception(e, source)

    def __iter__(self):
        # TODO: Django allows iterating over the templates nodes. Should
        # be parse ourself and iterate over the AST?
        raise NotImplementedError()

    def render(self, context=None):
        '''Differs from Django's own render() slightly in that makes the
        ``context`` parameter optional. We try to strike a middle ground
        here between implementing Django's interface while still supporting
        Jinja's own call syntax as well.
        '''
        if not context:
            context = {}
        else:
            context = dict_from_django_context(context)

        try:
            return super(Template, self).render(context)
        except _jinja2_exceptions.TemplateSyntaxError, e:
            raise _generate_django_exception(e)
        except _jinja2_exceptions.UndefinedError, e:
            # UndefinedErrors don't have a source attribute so we create one
            import sys
            import traceback
            exc_traceback = sys.exc_info()[-1]
            trace = traceback.extract_tb(exc_traceback)[-1]
            e.lineno = trace[1]
            source = None

            # If we're getting <template> than we're being call from a memory
            # template, this occurs when we use the {% jinja %} template tag
            # In that case we use the Django source and find our position
            # within that
            if trace[0] == '<template>' and hasattr(self, 'source'):
                source = self.source
                e.name = source[0].name
                e.source = source
            else:
                e.name = trace[0]

            # We have to cleanup the trace manually, Python does _not_ clean
            # it up for us!
            del exc_traceback, trace

            raise _generate_django_exception(e, source)


def dict_from_django_context(context):
    '''Flattens a Django :class:`django.template.context.Context` object.'''
    if not isinstance(context, DjangoContext):
        return context
    else:
        dict_ = {}
        # Newest dicts are up front, so update from oldest to newest.
        for subcontext in reversed(list(context)):
            dict_.update(dict_from_django_context(subcontext))
        return dict_


# libraries to load by default for a new environment
builtins = []


def add_to_builtins(module_name):
    '''Add the given module to both Coffin's list of default template
    libraries as well as Django's. This makes sense, since Coffin
    libs are compatible with Django libraries.

    You can still use Django's own ``add_to_builtins`` to register
    directly with Django and bypass Coffin.

    TODO: Allow passing path to (or reference of) extensions and
    filters directly. This would make it easier to use this function
    with 3rd party Jinja extensions that do not know about Coffin and
    thus will not provide a Library object.

    XXX/TODO: Why do we need our own custom list of builtins? Our
    Library object is compatible, remember!? We can just add them
    directly to Django's own list of builtins.
    '''
    builtins.append(import_library(module_name))
    django_add_to_builtins(module_name)


add_to_builtins('coffin.template.defaulttags')
add_to_builtins('coffin.template.defaultfilters')
add_to_builtins('coffin.template.interop')

