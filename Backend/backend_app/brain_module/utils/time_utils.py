"""
Time helpers for provider usage resetting.
Uses local timezone naive midnight reset. You can adapt to utc if needed.
"""
import time
import datetime

def now_ts():
    return int(time.time())

def today_date_str():
    return datetime.date.today().isoformat()

def seconds_until_midnight():
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime.combine(tomorrow.date(), datetime.time.min)
    return int((midnight - now).total_seconds())