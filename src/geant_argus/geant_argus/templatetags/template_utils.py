from django import template
from django.utils.dateparse import parse_datetime


register = template.Library()


@register.filter
def get_item(obj, key):
    return _get_item(obj, key)


def _get_item(obj, *keys):
    if obj is None:
        return None
    if not len(keys):
        return None
    key, *rest = keys
    result = obj.get(key, None) if isinstance(obj, dict) else getattr(obj, key, None)
    if not rest:
        return result
    return _get_item(result, *rest)


@register.filter
def get_quick_glance_item(obj, key):
    value = _get_item(obj, *key.split("."))

    if isinstance(value, list):
        return " - ".join(str(v) for v in value)

    return value


@register.filter
def dateparse(datestr):
    if not isinstance(datestr, str):
        return None
    return parse_datetime(datestr)


@register.filter
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    parts = []
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = int(secs // 86400)
        parts.append(f"{days}d")
        secs = secs - days * 86400

    if secs > 3600:
        hrs = int(secs // 3600)
        parts.append(f"{hrs}h")
        secs = secs - hrs * 3600

    if secs > 60:
        mins = int(secs // 60)
        parts.append(f"{mins}m")
        secs = secs - mins * 60

    if secs > 0:
        parts.append(f" {int(secs)}s")
    return " ".join(parts)


@register.filter
def underscores_to_spaces(value):
    if not isinstance(value, str):
        return value
    return value.replace("_", " ")
