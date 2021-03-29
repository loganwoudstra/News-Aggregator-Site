from django import template

register = template.Library()

@register.filter
def get_attr(user, company):
    return getattr(user, company)