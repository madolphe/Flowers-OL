from django import forms
from django.template import loader
from django.utils.safestring import mark_safe


class rangeLikert(forms.Widget):
    template_name = 'includes/rangeLikert.html'
    input_type = 'range'
    needs_validator = True

    def get_context(self, name, value, attrs):
        context = super(rangeLikert, self).get_context(name, value, attrs)
        context['widget']['attrs']['prompt'] = self.attrs['prompt']
        context['widget']['attrs']['annotations'] = self.attrs['annotations']
        context['widget']['attrs']['min_'] = self.attrs['min_']
        context['widget']['attrs']['max_'] = self.attrs['max_']
        context['widget']['attrs']['step'] = self.attrs['step']
        return context

    def render(self, name, value, attrs, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class polarLikert(rangeLikert):
    template_name = 'includes/polarLikert.html'
    input_type = 'range'

    def get_context(self, name, value, attrs):
        context = super(rangeLikert, self).get_context(name, value, attrs)
        context['widget']['attrs']['inner_range'] = self.attrs['inner_range']
        return context


class basicLikert(rangeLikert):
    template_name = 'includes/basicLikert.html'
    input_type = 'radio'
    needs_validator = False

    def get_context(self, name, value, attrs):
        context = super(rangeLikert, self).get_context(name, value, attrs)
        context['widget']['attrs']['header'] = self.attrs['header']
        context['widget']['attrs']['options'] = self.attrs['options']
        context['widget']['attrs']['checked'] = self.attrs['checked']
        return context


def get_custom_Likert_widget(question_object, index=False):
    pre = '{}. '.format(index) if index else ''
    odd = False
    if index:
        odd = not (index % 2 == 0)
    if question_object.widget == 'range':
        return rangeLikert(attrs={
            'prompt': pre + question_object.prompt,
            'annotations': question_object.annotations.split('~'),
            'min_': question_object.min_val,
            'max_': question_object.max_val,
            'step': question_object.step,
            'class': question_object.widget})
    if question_object.widget == 'polar':
        return polarLikert(attrs={
            'prompt': pre + question_object.prompt,
            'annotations': question_object.annotations.split('~'),
            'min_': question_object.min_val,
            'max_': question_object.max_val,
            'step': question_object.step,
            'inner_range': range(question_object.max_val-2),
            'class': question_object.widget})
    if question_object.widget == 'likert':
        annotations = []
        for a in question_object.annotations.split('~'): annotations.append(a if a else ' ')
        return basicLikert(attrs={
            'prompt': pre + question_object.prompt,
            'annotations': annotations,
            'header': True if index==1 else False,
            'options': list(range(question_object.min_val, question_object.max_val+1)),
            'checked': None,
            'handle': question_object.handle,
            'odd': odd})
