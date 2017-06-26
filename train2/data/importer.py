import datetime
import json
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
    # LOGGER.info("Created trip %s", trip)
    return trip


def assert_valid_dates(exp_arrival, actual_arrival, exp_departure, actual_departure):
    for dt in exp_arrival, actual_arrival, exp_departure, actual_departure:
        assert (dt is None or isinstance(dt, datetime.datetime)
                and dt.tzinfo and dt.tzinfo.zone == 'Asia/Jerusalem'), 'illegal dt = {}'.format(dt)


@transaction.atomic
def create_sample(*,
                  trip,
                  is_source,
                  is_dest,
                  gtfs_stop_id,
                  gtfs_stop_name,
                  exp_arrival,
                  actual_arrival,
                  exp_departure,
                  actual_departure,
                  index,
                  filename,
                  sheet_idx,
                  line_number,
                  valid,
                  invalid_reason):
    assert_valid_dates(exp_arrival, actual_arrival, exp_departure, actual_departure)

    if exp_arrival and actual_arrival:
        delay_arrival = (actual_arrival - exp_arrival).total_seconds()
    else:
        delay_arrival = None

    if exp_departure and actual_departure:
        delay_departure = (actual_departure - exp_departure).total_seconds()
    else:
        delay_departure = None

    assert isinstance(index, int) and index > 0
    assert isinstance(filename, str)
    assert isinstance(line_number, int) and line_number >= 0
    try:
        stop = models.Stop.objects.get(gtfs_stop_id=gtfs_stop_id)
    except models.Stop.DoesNotExist:
        proposal = {
            "stop_short_name": gtfs_stop_name,
            "gtfs_stop_id": gtfs_stop_id,
            "latlon": [
                0,
                0
            ],
            "bssids": [],
            "stop_name": "INSERT ENGLISH NAME",
        }
        raise ValueError("Failed to find stop with gtfs_stop_id = {}\n{}\n{}".format(
            gtfs_stop_id,
            gtfs_stop_name,
            json.dumps(proposal, indent=4)))
    if not trip.samples.filter(stop_id=stop.id).exists():
        sample = models.Sample.objects.create(trip=trip,
                                              stop=stop,
                                              gtfs_stop_id=stop.gtfs_stop_id,
                                              is_source=is_source,
                                              is_dest=is_dest,
                                              exp_arrival=exp_arrival,
                                              actual_arrival=actual_arrival,
                                              delay_arrival=delay_arrival,
                                              exp_departure=exp_departure,
                                              actual_departure=actual_departure,
                                              delay_departure=delay_departure,
                                              index=index,
                                              filename=filename,
                                              sheet_idx=sheet_idx,
                                              line_number=line_number,
                                              valid=valid,
                                              invalid_reason=invalid_reason
                                              )
    else:
        trip.set_invalid("skipped non unique sample")
        return None

    return sample
