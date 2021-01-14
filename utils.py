import datetime
from datetime import datetime


def timestamp_to_string(timestampToConvert, format="%Y-%m-%d %H:%M:%S"):
    return datetime.utcfromtimestamp(timestampToConvert / 1000).strftime(format)


def datetime_to_string(datetimeToConvert, format="%Y-%m-%d %H:%M:%S"):
    ts = datetime_to_timestamp(datetimeToConvert) * 1000
    return timestamp_to_string(ts, format)


def timestamp_to_datetime(timestampToConvert) -> datetime:
    return datetime.utcfromtimestamp(timestampToConvert / 1000)


def datetime_to_timestamp(datetimeToConvert):
    return datetimeToConvert.timestamp()

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month