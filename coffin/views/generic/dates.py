from coffin.views.generic.detail import SingleObjectTemplateResponseMixin
from coffin.views.generic.list import MultipleObjectTemplateResponseMixin
import django.views.generic.dates as _generic_dates

class ArchiveIndexView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseArchiveIndexView):
    """
    Equivalent of django generic view ArchiveIndexView, but uses Jinja template renderer.
    """
    template_name_suffix = '_archive'


class YearArchiveView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseYearArchiveView):
    """
    Equivalent of django generic view YearArchiveView, but uses Jinja template renderer.
    """
    template_name_suffix = '_archive_year'


class MonthArchiveView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseMonthArchiveView):
    """
    Equivalent of django generic view MonthArchiveView, but uses Jinja template renderer.
    """
    template_name_suffix = '_archive_month'


class WeekArchiveView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseWeekArchiveView):
    """
    Equivalent of django generic view WeekArchiveView, but uses Jinja template renderer.
    """
    template_name_suffix = '_archive_week'


class DayArchiveView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseDayArchiveView):
    """
    Equivalent of django generic view DayArchiveView, but uses Jinja template renderer.
    """
    template_name_suffix = "_archive_day"

class TodayArchiveView(MultipleObjectTemplateResponseMixin, _generic_dates.BaseTodayArchiveView):
    """
    Equivalent of django generic view TodayArchiveView, but uses Jinja template renderer.
    """
    template_name_suffix = "_archive_day"


class DateDetailView(SingleObjectTemplateResponseMixin, _generic_dates.BaseDateDetailView):
    """
    Equivalent of django generic view DateDetailView, but uses Jinja template renderer.
    """
    template_name_suffix = '_detail'