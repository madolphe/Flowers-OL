from modeltranslation.translator import translator, TranslationOptions
from .models import Study


class StudyTranslationOptions(TranslationOptions):
    fields = ['project']


class TaskTranslationOptions(TranslationOptions):
    fields = ['prompt', 'description']


translator.register(Study, StudyTranslationOptions)
translator.register(Task, TaskTranslationOptions)
