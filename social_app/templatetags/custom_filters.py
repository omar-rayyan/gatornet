from django import template
from datetime import timedelta, datetime
from django.utils.timezone import now

register = template.Library()

@register.filter
def abbreviate_number(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M".rstrip('0').rstrip('.')
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k".rstrip('0').rstrip('.')
        else:
            return str(value)
    except (ValueError, TypeError):
        return value
    
@register.filter
def time_ago(value):
    current_time = now()
    if isinstance(value, datetime):
        diff = current_time - value

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            return f"{int(diff.total_seconds() // 60)}m ago"
        elif diff < timedelta(days=1):
            return f"{int(diff.total_seconds() // 3600)}h ago"
        elif diff < timedelta(days=30):
            return f"{int(diff.days)}d ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"
    return value