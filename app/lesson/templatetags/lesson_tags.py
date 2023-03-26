from django import template


register = template.Library()


@register.filter
def cut_example(text, arg):
    try:
        text = text.split('—')
        res = text[int(arg)]
    except Exception:
        return '—'
    return res
