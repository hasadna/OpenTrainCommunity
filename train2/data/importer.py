import datetime

import logging
import pytz
from django.db import transaction

LOGGER = logging.getLogger(__name__)
ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')

from . import models

@transaction.atomic
def create_trip(*,
                train_num,
                date):
    assert isinstance(date, datetime.date)
    assert isinstance(train_num, int) and train_num > 0
    trip = models.Trip.objects.create(train_num=train_num,
                                      date=date)
    #LOGGER.info("Created trip %s", trip)
    return trip


def assert_valid_dates(exp_arrival, actual_arrival, exp_departure, actual_departure):
    for dt in exp_arrival, actual_arrival, exp_departure, actual_departure:
        assert (dt is None or isinstance(dt, datetime.datetime)
                and dt.tzinfo and dt.tzinfo.zone == 'Asia/Jerusalem'),'illegal dt = {}'.format(dt)


@transaction.atomic
def create_sample(*,
                  trip,
                  is_source,
                  is_dest,
                  gtfs_stop_id,
                  exp_arrival,
                  actual_arrival,
                  exp_departure,
                  actual_departure,
                  index,
                  filename,
                  line_number,
                  valid,
                  invalid_reason):
    assert_valid_dates(exp_arrival, actual_arrival, exp_departure, actual_departure)
    assert isinstance(index, int) and index > 0
    assert isinstance(filename, str)
    assert isinstance(line_number, int) and line_number > 0
    try:
        stop = models.Stop.objects.get(gtfs_stop_id=gtfs_stop_id)
    except models.Stop.DoesNotExist:
        raise ValueError("Failed to find stop with gtfs_stop_id = {}".format(gtfs_stop_id))
    sample = models.Sample.objects.create(trip=trip,
                                          stop=stop,
                                          is_source=is_source,
                                          is_dest=is_dest,
                                          exp_arrival=exp_arrival,
                                          actual_arrival=actual_arrival,
                                          exp_departure=exp_departure,
                                          actual_departure=actual_departure,
                                          index=index,
                                          filename=filename,
                                          line_number=line_number,
                                          valid=valid,
                                          invalid_reason=invalid_reason
                                          )
    return sample