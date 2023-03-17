from django import template


register = template.Library()


@register.filter
def cut_example(text, arg):
    text = text.split('—')
    print(text)
    return text[int(arg)]
