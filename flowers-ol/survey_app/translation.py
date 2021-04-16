from modeltranslation.translator import translator, TranslationOptions
from .models import Question

class QuestionTranslationOptions(TranslationOptions):
    fields = ('prompt', 'annotations')

translator.register(Question, QuestionTranslationOptions)