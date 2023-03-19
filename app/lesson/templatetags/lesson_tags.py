from django import template


register = template.Library()


@register.filter
def cut_example(text, arg):
    text = text.split('—')
    return text[int(arg)]
