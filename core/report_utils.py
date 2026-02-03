from datetime import timedelta
from django.utils import timezone

def get_week_range(date):
    """
    Returns start and end date of the week for given date.
    Week starts on Monday and ends on Sunday.
    """
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range(date):
    """
    Returns first and last date for the month of given date.
    """
    start = date.replace(day=1)

    # Move to next month start then subtract 1 day
    if date.month == 12:
        next_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        next_month = date.replace(month=date.month + 1, day=1)

    end = next_month - timedelta(days=1)
    return start, end
