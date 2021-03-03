from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def contains(list_, value):
    return str(value) in list_ if list_ is not None else False
