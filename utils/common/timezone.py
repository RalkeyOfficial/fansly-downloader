import time


# calculates offset from global utc time, to local systems time
def compute_timezone_offset():
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    diff_from_utc = int(offset / 60 / 60 * -1)
    hours_in_seconds = diff_from_utc * 3600 * -1
    return diff_from_utc, hours_in_seconds


# detect 12 vs 24 hour time format usage (not sure if this properly works)
time_format = 12 if ('AM' in time.strftime('%X') or 'PM' in time.strftime('%X')) else 24


# convert every epoch timestamp passed, to the time it was for the local computers timezone
def get_adjusted_datetime(epoch_timestamp: int, diff_from_utc: int = diff_from_utc, hours_in_seconds: int = hours_in_seconds):
    adjusted_timestamp = epoch_timestamp + diff_from_utc * 3600
    adjusted_timestamp += hours_in_seconds
    # start of strings are ISO 8601; so that they're sortable by Name after download
    if time_format == 24:
        return time.strftime("%Y-%m-%d_at_%H-%M", time.localtime(adjusted_timestamp))
    else:
        return time.strftime("%Y-%m-%d_at_%I-%M-%p", time.localtime(adjusted_timestamp))
