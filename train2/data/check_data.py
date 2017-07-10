import datetime

from . import models

# Run using:
# python manage.py check

MIN_MONTH = 6
MAX_MONTH = 6
MIN_MONTHLY_TRIP_COUNT = 8000
MAX_MONTHLY_TRIP_COUNT = 15000
MIN_DAILY_TRIP_COUNT = 100
MIN_DAILY_TRIP_COUNT_SAT = 20
MAX_DAILY_TRIP_COUNT = 500
MIN_MONTHLY_VALID_TRIP_RATIO = 0.97
MIN = 0
MAX = 1
ZERO_STOPS = [
    'Achihud', ''
]
BIG_STOPS = [
    'Tel Aviv - University',
    'Tel Aviv Center - Savidor',
    'Leb Hmifratz',
    'Tel Aviv HaShalom',
    'Tel Aviv HaHagana',
    'Hutsot HaMifrats',
    'Akko',
    'Nahariyya',
    'Haifa Center HaShmona',
    "Haifa Hof HaKarmel (Razi'el)",
    'Binyamina',
    'Haifa Bat Gallim',
    'Lod',
    'Herzliyya',
]

MEDIUM_STOPS = [
    'Modiin',
    'Modiin Center',
    'Kiryat Hayyim',
    'Atlit',
]


MONTHLY_SAMPLES = {
    'default': [150, 3000],
    'Jerusalem Malha': [20, 800],
    'Jerusalem Biblical Zoo': [20, 300],
    'Dimona': [30, 300]
}


for st in BIG_STOPS:
    MONTHLY_SAMPLES[st] = [1200, 6000]

for st in MEDIUM_STOPS:
    MONTHLY_SAMPLES[st] = [800, 2500]

for st in models.Stop.objects.all():
    if 'tel aviv' in st.english.lower():
        MONTHLY_SAMPLES[st.english] = [4000, 12000]


class Error:
    def __init__(self, code, text):
        self.code = code
        self.text = text

    MONTH_TRIP_COUNT_TOO_LOW = 'MONTH_TRIP_COUNT_TOO_LOW'
    MONTH_TRIP_COUNT_TOO_HIGH = 'MONTH_TRIP_COUNT_TOO_HIGH'
    MONTH_DAY_COUNT_TOO_LOW = 'MONTH_DAY_COUNT_TOO_LOW'
    MONTH_DAY_COUNT_TOO_HIGH = 'MONTH_DAY_COUNT_TOO_HIGH'
    VALID_TRIP_RATIO_TOO_LOW = 'VALID_TRIP_RATIO_TOO_LOW'
    SAMPLES_COUNT_PER_STOP_TOO_LOW = 'SAMPLES_COUNT_PER_STOP_TOO_LOW'
    SAMPLES_COUNT_PER_STOP_TOO_HIGH = 'SAMPLES_COUNT_PER_STOP_TOO_HIGH'

    @classmethod
    def error_codes(cls):
        return [k for k in cls.__dict__.keys()
                if k.upper() == k and isinstance(getattr(cls, k), str)]


def run():
    errors = []
    errors.extend(check_months())
    # TODO: Enable this once we get daily data for Jan-Mar 2017
    errors.extend(check_days())
    errors.extend(check_valid_percent_per_month())
    errors.extend(check_samples_per_station_per_month())

    errors_by_code = {c: [] for c in Error.error_codes()}
    for error in errors:
        errors_by_code[error.code].append(error)

    print("=" * 80)
    print("= SUMMARY")
    print("-------------------")
    for code, code_errors in sorted(errors_by_code.items(),
                                    key=lambda x: len(x[1]),
                                    reverse=True):
        print('{} :{}'.format(code, len(code_errors)))
    print("=" * 80)
    for code, code_errors in sorted(errors_by_code.items(),
                                    key=lambda x: len(x[1]),
                                    reverse=True):
        if code_errors:
            print('{} : {} errors'.format(code, len(code_errors)))
            print('-' * 50)
        for code_error in code_errors:
            print(code_error.text)
        if code_errors:
            print('=' * 80)


def check_months():
    errors = []
    for month in range(MIN_MONTH, MAX_MONTH+1):
        print('Checking month', month)
        date1 = datetime.datetime(2017, month, 1)
        date2 = datetime.datetime(2017, month + 1, 1)
        trip_count = models.Trip.objects.filter(date__gte=date1, date__lt=date2).count()
        if trip_count < MIN_MONTHLY_TRIP_COUNT:
            errors.append(Error(Error.MONTH_TRIP_COUNT_TOO_LOW,
                                "Trip count {} for month {} is lower than minimum {}".format(trip_count, month,
                                                                                             MIN_MONTHLY_TRIP_COUNT)))
        if trip_count > MAX_MONTHLY_TRIP_COUNT:
            errors.append(Error(Error.MONTH_TRIP_COUNT_TOO_HIGH,
                                "Trip count {} for month {} is higher than maximum {}".format(trip_count, month,
                                                                                              MAX_MONTHLY_TRIP_COUNT)))
    return errors


def check_days():
    errors = []
    date1 = datetime.datetime(2017, MIN_MONTH, 1)
    date2 = datetime.datetime(2017, MAX_MONTH + 1, 1)
    for day in daterange(date1, date2):
        min_daily_count = MIN_DAILY_TRIP_COUNT
        if day.weekday() == 5:
            min_daily_count = MIN_DAILY_TRIP_COUNT_SAT

        trip_count = models.Trip.objects.filter(date__gte=day, date__lt=day + datetime.timedelta(days=1)).count()
        if trip_count < min_daily_count:
            errors.append(Error(Error.MONTH_DAY_COUNT_TOO_LOW,
                                "Trip count {} for day {} is lower than minimum {}".format(trip_count, day,
                                                                                           MIN_DAILY_TRIP_COUNT)))
        if trip_count > MAX_DAILY_TRIP_COUNT:
            errors.append(Error(Error.MONTH_DAY_COUNT_TOO_HIGH,
                                "Trip count {} for day {} is higher than maximum {}".format(trip_count, day,
                                                                                            MAX_DAILY_TRIP_COUNT)))
    return errors


def check_valid_percent_per_month():
    errors = []
    for month in range(1, MAX_MONTH + 1):
        date1 = datetime.datetime(2017, month, 1)
        date2 = datetime.datetime(2017, month + 1, 1)
        all_trip_count = models.Trip.objects.filter(date__gte=date1, date__lt=date2).count()
        valid_trip_count = models.Trip.objects.filter(date__gte=date1, date__lt=date2, valid=True).count()
        if all_trip_count:
            valid_trip_ratio = valid_trip_count / all_trip_count
        else:
            valid_trip_ratio = 0
        if valid_trip_ratio < MIN_MONTHLY_VALID_TRIP_RATIO:
            errors.append(Error(Error.VALID_TRIP_RATIO_TOO_LOW,
                                "Valid trip ratio {} for month {} is lower than minimum {}".format(
                                    valid_trip_ratio, month, MIN_MONTHLY_VALID_TRIP_RATIO)))
    return errors


def check_samples_per_station_per_month():
    errors = []
    stops = [st for st in models.Stop.objects.all() if st.english not in ZERO_STOPS]
    for month in range(MIN_MONTH, MAX_MONTH + 1):
        for stop in stops:
            date1 = datetime.datetime(2017, month, 1)
            date2 = datetime.datetime(2017, month + 1, 1)
            samples_count = models.Sample.objects.filter(trip__date__gte=date1, trip__date__lt=date2,
                                                         stop__gtfs_stop_id=stop.gtfs_stop_id).count()
            min_monthly_samples = MONTHLY_SAMPLES[stop.english][MIN] if stop.english in MONTHLY_SAMPLES else \
                MONTHLY_SAMPLES['default'][MIN]
            max_monthly_samples = MONTHLY_SAMPLES[stop.english][MAX] if stop.english in MONTHLY_SAMPLES else \
                MONTHLY_SAMPLES['default'][MAX]
            if samples_count < min_monthly_samples:
                errors.append(Error(Error.SAMPLES_COUNT_PER_STOP_TOO_LOW,
                                    "Samples count {} on month {} for stop {} ({}) is lower than minimum {}".format(
                                        samples_count,
                                        month,
                                        stop.gtfs_stop_id,
                                        stop.english,
                                        min_monthly_samples)))
            if samples_count > max_monthly_samples:
                errors.append(Error(Error.SAMPLES_COUNT_PER_STOP_TOO_HIGH,
                                    "Samples count {} on month {} for stop {} ({}) is higher than maximum {}".format(
                                        samples_count,
                                        month,
                                        stop.gtfs_stop_id,
                                        stop.english,
                                        max_monthly_samples)))
    return errors


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)
