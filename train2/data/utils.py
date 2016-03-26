import calendar
import datetime


def encode_date(date):
    if date is None:
        return None

    assert isinstance(date, (datetime.datetime, datetime.date)), date

    if hasattr(date, 'utcoffset') and date.utcoffset:
        date -= date.utcoffset() or 0

    millis = int(calendar.timegm(date.timetuple()) * 1000)
    return millis