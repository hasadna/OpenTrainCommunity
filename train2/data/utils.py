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


def parse_date(dt_str):
    if dt_str is None:
        return None

    if dt_str.isdigit():
        timestamp = int(dt_str)
        if timestamp > 1e12:  # java time, with milliseconds
            timestamp /= 1000
        return datetime.datetime.fromtimestamp(timestamp)

    try:
        d, m, y = [int(x) for x in dt_str.split('/')]
        if y < 2013:
            raise ValueError('Wrong year %s for param %s' % (y, dt_str))
        return datetime.datetime(year=y, month=m, day=d)
    except ValueError as e:
        raise ValueError('Wrong date param %s: %s' % (dt_str, str(e)))
