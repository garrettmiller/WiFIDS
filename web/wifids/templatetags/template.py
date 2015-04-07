from django import template

register = template.Library()

def lookup(d, key):
    return d[key]


register.filter('lookup', lookup)