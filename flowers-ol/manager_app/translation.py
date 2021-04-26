from modeltranslation.translator import translator, TranslationOptions
from .models import Study, Task


class StudyTranslationOptions(TranslationOptions):
    fields = ['project']


class TaskTranslationOptions(TranslationOptions):
    fields = ['prompt', 'description','actions']


translator.register(Study, StudyTranslationOptions)
translator.register(Task, TaskTranslationOptions)
