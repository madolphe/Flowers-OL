from modeltranslation.translator import translator, TranslationOptions
from .models import CognitiveTask


class CognitiveTaskTranslationOptions(TranslationOptions):
    fields = ['name']


translator.register(CognitiveTask, CognitiveTaskTranslationOptions)