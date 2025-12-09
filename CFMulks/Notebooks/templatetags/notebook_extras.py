import markdown2

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='render_markdown')
@stringfilter
def render_markdown(value):
    result = markdown2.markdown(value, extras={'break-on_backslash': True, 'tables': None, 'strike': None})
    return mark_safe(result)

@register.filter(name='render_texdown')
@stringfilter
def render_texdown(value):
    result = markdown2.markdown(value, extras={'break-on_backslash': True, 'latex': None, 'tables': None, 'strike': None})
    return mark_safe(result)

@register.filter(name='render_tags')
def render_tags(value):
    result = ", ".join(list(value.names()))
    if result == '':
        result = "No Tags"
    return mark_safe(result)