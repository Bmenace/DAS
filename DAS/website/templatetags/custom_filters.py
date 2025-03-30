from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def dict_key(d, key):
    """Returns value from dictionary using a key, or an empty string if key is missing"""
    return d.get(key, "")


@register.filter
def split(value, delimiter):
    """Split a string by a delimiter."""
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    return dictionary.get(key, None)