from django import template
import os

register = template.Library()

@register.simple_tag
def nav_urls (symbol, interval):
    return os.path.join('/',symbol,interval) 
