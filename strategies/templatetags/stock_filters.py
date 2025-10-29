"""
Custom template filters for stock data formatting
"""
from django import template
from strategies.stock_data import format_volume as _format_volume

register = template.Library()


@register.filter(name='format_volume')
def format_volume(volume):
    """
    Format volume with K/M/B suffixes

    Usage in template: {{ mover.pre_market_volume|format_volume }}
    """
    return _format_volume(volume)
