from modeltranslation.translator import TranslationOptions, translator

from .models import Study, Task


class StudyTranslationOptions(TranslationOptions):
    fields = ['project']


class TaskTranslationOptions(TranslationOptions):
    fields = ['prompt', 'description','actions','info_templates_csv']


translator.register(Study, StudyTranslationOptions)
translator.register(Task, TaskTranslationOptions)
