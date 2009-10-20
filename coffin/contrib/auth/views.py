import inspect

from django.contrib.auth.views import *

# XXX: maybe approach this as importing the entire model, and doing string replacements
# on the template and shortcut import lines?

from coffin.shortcuts import render_to_response
from coffin.template import RequestContext, loader

exec inspect.getsource(logout)
exec inspect.getsource(password_change_done)
exec inspect.getsource(password_reset)
exec inspect.getsource(password_reset_confirm)
exec inspect.getsource(password_reset_done)
exec inspect.getsource(password_reset_complete)

exec inspect.getsource(password_change.view_func)
password_change = login_required(password_change)

# XXX: this function uses a decorator, which calls functools.wraps, which compiles the code
# thus we cannot inspect the source
def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action."
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request)
    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
login = never_cache(login)