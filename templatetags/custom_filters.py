from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def upto(value, delimiter=','):
    return value.split(delimiter)[0]
upto.is_safe = True