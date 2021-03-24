from django.contrib import admin
from .models import *
# from ..mot_app.models import *
from django.contrib.sessions.models import Session
from .utils import ExportCsvMixin


# Define admin classes
class ParticipantAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('user', 'study', 'date', 'current_session', 'task_stack_csv', 'extra_json')
    actions = ["export_as_csv"]


# Register your models here
admin.site.register(Session)
admin.site.register(Study)
admin.site.register(ParticipantProfile, ParticipantAdmin)
admin.site.register(ExperimentSession)
admin.site.register(Task)
