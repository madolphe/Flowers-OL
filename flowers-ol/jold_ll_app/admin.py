from django.contrib import admin
from .models import *
from manager_app import utils as manager_app_utils


class JOLD_LL_trialAdmin(admin.ModelAdmin, manager_app_utils.ExportCsvMixin):
    list_display = ('participant', 'session', 'forced', 'trial', 'wind', 'outcome', 'init_dist', 'end_dist', 'time_trial', 'presses', 'fuel')
    list_filter = ['participant', 'session', 'forced']
    actions = ["export_as_csv"]


# Register your models here.
admin.site.register(JOLD_LL_trial, JOLD_LL_trialAdmin)
