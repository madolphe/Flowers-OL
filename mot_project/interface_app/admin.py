from django.contrib import admin
from .models import *
from django.contrib.sessions.models import Session

# Define admin classes
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'study', 'date', 'current_session', 'task_stack_csv', 'extra_json')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'participant', 'question', 'session', 'value')


# Register your models here
admin.site.register(Session)
admin.site.register(Study)
admin.site.register(JOLD_LL_trial)
admin.site.register(Question)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ParticipantProfile, ParticipantAdmin)
admin.site.register(ExperimentSession)
admin.site.register(Task)
