from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Template tag to replace GET parameters in URL while keeping existing ones.
    Usage: {% url_replace page=2 %}
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()

@register.filter
def percentage(value, total):
    """
    حساب النسبة المئوية
    مثال: {{ value|percentage:total }}
    """
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0
