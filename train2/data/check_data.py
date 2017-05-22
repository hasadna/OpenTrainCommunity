from . import models
import datetime


MAX_MONTH = 3
MIN_MONTHLY_TRIP_COUNT = 2500
MAX_MONTHLY_TRIP_COUNT = 3500
MIN_DAILY_TRIP_COUNT = 100
MAX_DAILY_TRIP_COUNT = 200

def run():
  check_months()
  check_days()

def check_months():
  errors = []
  for month in range(1, MAX_MONTH + 1):
    date1 = datetime.datetime(2017, month, 1)
    date2 = datetime.datetime(2017, month + 1, 1)
    trip_count = models.Trip.objects.filter(date__gte=date1, date__lt=date2).count()
    if trip_count < MIN_MONTHLY_TRIP_COUNT:
      errors.append("Trip count {} for month {} is lower than minimum {}".format(trip_count, month, MIN_MONTHLY_TRIP_COUNT))
    if trip_count > MAX_MONTHLY_TRIP_COUNT:
      errors.append("Trip count {} for month {} is higher than maximum {}".format(trip_count, month, MAX_MONTHLY_TRIP_COUNT))
  if errors:
    for error in errors:
      print(error)
  else:
    print("No errors in months")


def check_days():
  errors = []
  date1 = datetime.datetime(2017, 1, 1)
  date2 = datetime.datetime(2017, MAX_MONTH + 1, 1)    
  for day in daterange(date1, date2):
    trip_count = models.Trip.objects.filter(date__gte=day, date__lt=day + datetime.timedelta(days=1)).count()
    if trip_count < MIN_DAILY_TRIP_COUNT:
      errors.append("Trip count {} for day {} is lower than minimum {}".format(trip_count, day, MIN_DAILY_TRIP_COUNT))
    if trip_count > MAX_DAILY_TRIP_COUNT:
      errors.append("Trip count {} for day {} is higher than maximum {}".format(trip_count, day, MAX_DAILY_TRIP_COUNT))
  if errors:
    for error in errors:
      print(error)
  else:
    print("No errors in days")

def daterange(start_date, end_date):
  for n in range(int ((end_date - start_date).days)):
    yield start_date + datetime.timedelta(n)
