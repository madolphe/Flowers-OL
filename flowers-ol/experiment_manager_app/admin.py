from django.contrib import admin
from .models import *
# from ..mot_app.models import *
from django.contrib.sessions.models import Session
from .utils import ExportCsvMixin

# Define admin classes
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'study', 'date', 'current_session', 'task_stack_csv', 'extra_json')


class JOLD_LL_trialAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('participant', 'session', 'forced', 'trial', 'wind', 'outcome', 'init_dist', 'end_dist', 'time_trial', 'presses', 'fuel')
    list_filter = ['participant', 'session', 'forced']
    actions = ["export_as_csv"]


# Register your models here
admin.site.register(Session)
admin.site.register(Study)
admin.site.register(JOLD_LL_trial, JOLD_LL_trialAdmin)
admin.site.register(ParticipantProfile, ParticipantAdmin)
admin.site.register(ExperimentSession)
admin.site.register(Task)
# admin.site.register(Episode, EpisodeAdmin)
