from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import *
from .utils import ExportCsvMixin


# Define admin classes
class ParticipantAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "user",
        "origin_timestamp",
        "session_stack_csv",
        "current_session",
        "task_stack",
        "extra_json",
    )
    actions = ["export_as_csv"]


# Register your models here
admin.site.register(Session)
admin.site.register(Study)
admin.site.register(ParticipantProfile, ParticipantAdmin)
admin.site.register(ExperimentSession)
admin.site.register(Task)
