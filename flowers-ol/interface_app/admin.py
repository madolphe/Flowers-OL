from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session
import csv
from django.http import HttpResponse


class ExportCsvMixin:
    """
    Export model as csv
    (Snapshot found in https://readthedocs.org/projects/django-admin-cookbook/downloads/pdf/latest/)
    """
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = "Export Selected"


# Define admin classes
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'study', 'date', 'current_session', 'task_stack_csv', 'extra_json')


class AnswerAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('__str__', 'participant', 'question', 'session', 'value')
    list_filter = ['participant']
    actions = ["export_as_csv"]


class EpisodeAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('__str__', 'participant', 'get_results', 'n_targets', 'n_distractors', 'probe_time',
                    'tracking_time', 'speed_max')
    list_filter = ['participant']
    actions = ["export_as_csv"]


class QuestionAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('handle', 'instrument', 'component', 'prompt', 'widget', 'type')
    list_filter = ['instrument', 'widget', 'type']
    actions = ["export_as_csv"]


class JOLD_LL_trialAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('participant', 'session', 'forced', 'trial', 'wind', 'outcome', 'init_dist', 'end_dist', 'time_trial', 'presses', 'fuel')
    list_filter = ['participant', 'session', 'forced']
    actions = ["export_as_csv"]


# Register your models here
admin.site.register(Session)
admin.site.register(Study)
admin.site.register(JOLD_LL_trial, JOLD_LL_trialAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ParticipantProfile, ParticipantAdmin)
admin.site.register(ExperimentSession)
admin.site.register(Task)
admin.site.register(Episode, EpisodeAdmin)
