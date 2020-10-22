from django import forms
from django.template import loader
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget, Select, NumberInput, TextInput, DateInput, SelectMultiple, MultiWidget, Textarea


class LikertRange(forms.Widget):
    template_name = 'includes/rangeLikert.html'
    input_type = 'range'
    needs_validator = True

    def get_context(self, name, value, attrs):
        context = super(LikertRange, self).get_context(name, value, attrs)
        context['widget']['attrs']['annotations'] = self.attrs['annotations']
        context['widget']['attrs']['min_'] = self.attrs['min_']
        context['widget']['attrs']['max_'] = self.attrs['max_']
        context['widget']['attrs']['step'] = self.attrs['step']
        return context

    def render(self, name, value, attrs, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class LikertPolar(LikertRange):
    template_name = 'includes/polarLikert.html'
    input_type = 'range'

    def get_context(self, name, value, attrs):
        context = super(LikertRange, self).get_context(name, value, attrs)
        context['widget']['attrs']['inner_range'] = self.attrs['inner_range']
        return context


class LikertBasic(LikertRange):
    template_name = 'includes/basicLikert.html'
    input_type = 'radio'
    needs_validator = False

    def get_context(self, name, value, attrs):
        context = super(LikertRange, self).get_context(name, value, attrs)
        context['widget']['attrs']['size'] = self.attrs['size']
        context['widget']['attrs']['options'] = self.attrs['options']
        context['widget']['attrs']['prev'] = self.attrs['prev']
        return context


class Categories(SelectMultiple):
    template_name = 'includes/categories.html'
    input_type = 'checkbox'
    needs_validator = False

    def get_context(self, name, value, attrs):
        context = super(SelectMultiple, self).get_context(name, value, attrs)
        context['widget']['attrs']['choices'] = self.attrs['choices']
        context['widget']['attrs']['size'] = self.attrs['size']
        context['widget']['attrs']['prev'] = self.attrs['prev']
        return context

    def render(self, name, value, attrs, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class CustomMultiWidget(MultiWidget):
    template_name = 'includes/multiwidget_screen.html'

    def __init__(self, attrs=None):
        choices = [('cm', 'cm'), ('inches', 'inches')]
        widgets = [
            TextInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=choices),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [*value]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        size, unit = super().value_from_datadict(data, files, name)
        try:
            if unit == 'inches':
                size = float(size)
                size *= 2.54
                size = str(size)
            return size
        except ValueError:
            return None


def get_custom_widget(question_object, num):
    if question_object.widget == 'custom-range':
        return LikertRange(attrs={
            'annotations': question_object.annotations.split('~'),
            'min_': question_object.min_val,
            'max_': question_object.max_val,
            'step': question_object.step,
            'class': question_object.widget})
    elif question_object.widget == 'custom-polar':
        return LikertPolar(attrs={
            'annotations': question_object.annotations.split('~'),
            'min_': question_object.min_val,
            'max_': question_object.max_val,
            'step': question_object.step,
            'inner_range': range(question_object.max_val-2),
            'class': question_object.widget})
    elif question_object.widget == 'custom-likert':
        annotations = []
        for a in question_object.annotations.split('~'): annotations.append(a if a else ' ')
        return LikertBasic(attrs={
            'options': [(i, a) for i, a in enumerate(question_object.annotations.split('~'))],
            'size': len(question_object.annotations.split('~')),
            'prev': None,
            'handle': question_object.handle,
            'odd': not (num % 2 == 0)})
    elif question_object.widget == 'custom-categories':
        return Categories(attrs={
            'choices': [(i, a) for i, a in enumerate(question_object.annotations.split('~'))],
            'size': len(question_object.annotations.split('~')),
            'prev': None,
            'handle': question_object.handle,
            'odd': not (num % 2 == 0)})
    elif question_object.widget == 'custom-textbox':
        return Textarea()
    elif question_object.widget == 'custom-float':
        return TextInput()
    elif question_object.widget == 'custom-int':
        return NumberInput()
    elif question_object.widget == 'custom-select':
        choices = question_object.annotations.split('~')
        choices = [(str(i), choices[i].capitalize()) for i in range(len(choices))]
        return Select(choices=choices)
    elif question_object.widget == 'custom-date':
        return DateInput()
    elif question_object.widget == 'multiple-widget':
        return CustomMultiWidget()
