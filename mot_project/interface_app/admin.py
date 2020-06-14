from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session

# Register your models here
admin.site.register(Session)
admin.site.register(StudySpec)
admin.site.register(Question)
admin.site.register(ParticipantProfile)
admin.site.register(ExperimentSession)
