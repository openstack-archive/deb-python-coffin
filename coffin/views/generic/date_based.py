from coffin.template import loader
from django.views.generic import date_based as _date_based
import functools


archive_index = functools.partial(_date_based.archive_index, template_loader=loader)
archive_year = functools.partial(_date_based.archive_year, template_loader=loader)
archive_month = functools.partial(_date_based.archive_month, template_loader=loader)
archive_week = functools.partial(_date_based.archive_week, template_loader=loader)
archive_daye = functools.partial(_date_based.archive_day, template_loader=loader)
archive_today = functools.partial(_date_based.archive_today, template_loader=loader)

object_detail = functools.partial(_date_based.object_detail, template_loader=loader)