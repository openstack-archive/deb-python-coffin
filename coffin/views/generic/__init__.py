from django.views.generic import GenericViewError
try:
    from django.views.generic.base import View, RedirectView
except ImportError:
    pass
else:
    from coffin.views.generic.base import TemplateView
    from coffin.views.generic.dates import (ArchiveIndexView, YearArchiveView,
                                            MonthArchiveView, WeekArchiveView,
                                            DayArchiveView, TodayArchiveView,
                                            DateDetailView)
    from coffin.views.generic.detail import DetailView
    from coffin.views.generic.edit import (FormView, CreateView, UpdateView,
                                           DeleteView)
    from coffin.views.generic.list import ListView
