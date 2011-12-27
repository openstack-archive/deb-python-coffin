from django.views.generic.dates import ArchiveIndexView as _ArchiveIndexView, YearArchiveIndexView as _YearArchiveIndexView 
from django.views.generic.dates import MonthArchiveIndexView as _MonthArchiveIndexView, WeekArchiveIndexView as _WeekArchiveIndexView
from django.views.generic.dates import DayArchiveIndexView as _DayArchiveIndexView, TodayArchiveIndexView as _TodayArchiveIndexView
from django.views.generic.dates import DateDetailView as _DateDetailView
from coffin.views.decorators import template_response

__all__ = ['ArchiveIndexView', 'YearArchiveIndexView', 'MonthArchiveIndexView', 'WeekArchiveIndexView',
        'DayArchiveIndexView', 'TodayArchiveIndexView', 'DateDetailView']

ArchiveIndexView, YearArchiveIndexView, MonthArchiveIndexView, WeekArchiveIndexView,\
        DayArchiveIndexView, TodayArchiveIndexView, DateDetailView = map(template_response,
            (_ArchiveIndexView, _YearArchiveIndexView, _MonthArchiveIndexView, _WeekArchiveIndexView,
        _DayArchiveIndexView, _TodayArchiveIndexView, _DateDetailView))

