import datetime
from datetime import datetime

def timestamp_to_string(timestampToConvert, format="%Y-%m-%d %H:%M:%S"):
    return datetime.utcfromtimestamp(timestampToConvert / 1000).strftime(format)

def datetime_to_string(datetimeToConvert, format="%Y-%m-%d %H:%M:%S"):
    ts = datetime_to_timestamp(datetimeToConvert)*1000
    return timestamp_to_string(ts, format)

def timestamp_to_datetime(timestampToConvert):
    return datetime.utcfromtimestamp(timestampToConvert / 1000)

def datetime_to_timestamp(datetimeToConvert):
    return datetimeToConvert.timestamp()