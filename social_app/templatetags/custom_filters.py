from django import template
from datetime import datetime, timedelta

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

def time_ago(value):
    now = datetime.now()
    if isinstance(value, datetime):
        diff = now - value

        if diff < timedelta(minutes=1):
            return f"{int(diff.total_seconds())}s ago"
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