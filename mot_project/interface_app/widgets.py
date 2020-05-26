from django import forms
from django.template import loader
from django.utils.safestring import mark_safe


class rangeLikert(forms.Widget):
    template_name = 'JOLD/rangeLikert.html'
    input_type = 'range'

    def get_context(self, name, value, attrs):
        context = super(rangeLikert, self).get_context(name, value, attrs)
        context['widget']['attrs']['annotations'] = self.attrs['annotations']
        context['widget']['attrs']['min_'] = self.attrs['min_']
        context['widget']['attrs']['max_'] = self.attrs['max_']
        context['widget']['attrs']['step'] = self.attrs['step']
        return context

    def render(self, name, value, attrs, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
