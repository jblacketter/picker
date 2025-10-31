"""
Custom template filters for stock data formatting
"""
from django import template
from strategies.stock_data import format_volume as _format_volume
from strategies.market_context import format_percent_change, get_change_color_class
from strategies.vwap_service import get_vwap_signal_color, format_vwap_signal

register = template.Library()


@register.filter(name='format_volume')
def format_volume(volume):
    """
    Format volume with K/M/B suffixes

    Usage in template: {{ mover.pre_market_volume|format_volume }}
    """
    return _format_volume(volume)


@register.filter(name='format_percent')
def format_percent(value):
    """
    Format percentage change with +/- sign

    Usage in template: {{ market_context.spy_change|format_percent }}
    Wave 2 Feature 2.1
    """
    return format_percent_change(value)


@register.filter(name='change_color_class')
def change_color_class(value):
    """
    Get Tailwind color class for positive/negative change

    Usage in template: <div class="{{ market_context.spy_change|change_color_class }}">
    Wave 2 Feature 2.1
    """
    return get_change_color_class(value)


@register.filter(name='vwap_signal_color')
def vwap_signal_color(vwap_data):
    """
    Get Tailwind color class for VWAP signal badge

    Usage in template: <div class="{{ vwap|vwap_signal_color }}">
    Wave 2 Feature 2.2
    """
    if not vwap_data:
        return ''
    return get_vwap_signal_color(vwap_data.signal, vwap_data.signal_strength)


@register.filter(name='vwap_signal_text')
def vwap_signal_text(vwap_data):
    """
    Format VWAP signal for display

    Usage in template: {{ vwap|vwap_signal_text }}
    Wave 2 Feature 2.2
    """
    if not vwap_data:
        return 'N/A'
    return format_vwap_signal(vwap_data.signal, vwap_data.distance_from_vwap)


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get item from dictionary by key

    Usage in template: {{ vwap_data|get_item:mover.id }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)
