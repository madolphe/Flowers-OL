from django.contrib import admin
from .models import *
from experiment_manager_app.utils import ExportCsvMixin


class AnswerAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('__str__', 'participant', 'question', 'session', 'value')
    list_filter = ['participant']
    actions = ["export_as_csv"]


class QuestionAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('handle', 'instrument', 'component', 'prompt', 'widget', 'type')
    list_filter = ['instrument', 'widget', 'type']
    actions = ["export_as_csv"]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)