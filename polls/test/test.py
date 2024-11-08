# from ... import views
# from views import format_timestamp
# from KU_DJANGO.polls.views import format_timestamp_

from datetime import timedelta
import datetime

dt = datetime.datetime

def format_timestamp(timestamp: datetime) -> str:
    """
    Formats a timestamp string into a human-readable format.

    Args:
        timestamp (str): The timestamp string in a suitable format (e.g., ISO 8601).

    Returns:
        str: The formatted timestamp string.
    """
    
    now = dt.now()
    time_diff = now - timestamp

    if time_diff.days == 0:
        if time_diff.seconds < 60:
            return f"{time_diff.seconds} seconds"
        if time_diff.seconds < 3600:
            return f"{time_diff.seconds // 60} minutes"
        else:
            return f"{time_diff.seconds // 3600} hours"
    elif time_diff.days < 7:
        return f"{time_diff.days} days"
    elif time_diff.days < 30:
        return f"{timestamp.strftime('%d %b')}"
    else:
        return f"{timestamp.strftime('%d %b %Y')}"

def test_seconds_ago():
    timestamp = dt.now() - timedelta(seconds=30)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == "30 seconds", "30 seconds"

def test_minutes_ago():
    timestamp = dt.now() - timedelta(minutes=30)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == "30 minutes", "30 minutes"

def test_hours_ago():
    timestamp = dt.now() - timedelta(hours=3)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == "3 hours", "3 hours"

def test_days_ago():
    timestamp = dt.now() - timedelta(days=2)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == "2 days", "2 days"

def test_dd_Mmm():
    timestamp = dt.now() - timedelta(days=29)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == timestamp.strftime('%d %b'), "dd Mmm" 
    print(formatted_time)

def test_dd_Mmm_yyyy():
    timestamp = dt.now() - timedelta(days=365)
    formatted_time = format_timestamp(timestamp)
    assert formatted_time == timestamp.strftime('%d %b %Y'), "dd Mmm yyyy" 
    print(formatted_time)

test_seconds_ago()
test_minutes_ago()
test_hours_ago()
test_days_ago()
test_dd_Mmm()
test_dd_Mmm_yyyy()
