import pytz
from django.db import transaction

import pandas as pd
import logging

import data.importer

from xlparser.utils_2015 import TripNumDate

LOGGER = logging.getLogger(__name__)

ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')


names = ["train_num",
         "planned_departure",
         "planned_arrival",
         "D",
         "is_planned",
         "actual_departure",
         "actual_arrival",
         "stop_id",
         "stop_name",
         "sequence_index",
         "K",
         "L",
         "is_commercial",
         "N",
         "trip_id",
         "route_name",
         "trip_date",
         "trip_type",
         "trip_year",
         "trip_month"]

@transaction.atomic
def parse_csv(csvname):
    df = pd.read_csv(csvname, names=names)
    for col in ["planned_departure",
                "planned_arrival",
                "actual_departure",
                "actual_arrival",
                "trip_date"]:
        df[col] = pd.to_datetime(df[col]).dt.tz_localize(ISRAEL_TIMEZONE)
    df.is_commercial = df.is_commercial == 'מסחרית'

    prev_trip_num_date = TripNumDate(num=None, date=None)
    created_ids = []
    for rowx, row in df.iterrows():
        if rowx % 1000 == 0:
            LOGGER.info("%s rows / %s", rowx, df.shape[0])
        cur_trip_num_date = TripNumDate(num=int(row.trip_id, row.trip_date.date()))
        if cur_trip_num_date != prev_trip_num_date:
            cur_trip = data.importer.create_trip(train_num=cur_trip_num_date.num,
                                                 date=cur_trip_num_date.date)
            created_ids.append(cur_trip.id)

        if row.is_commercial:
            try:
                data.importer.create_sample(trip=cur_trip,
                                            is_source=stop_kind.is_source,
                                            is_dest=stop_kind.is_dest,
                                            gtfs_stop_id=int(d['מספר תחנה']),
                                            exp_arrival=d['תאריך וזמן הגעת רכבת לתחנה מתוכנן'] or None,
                                            actual_arrival=d['תאריך וזמן הגעת רכבת לתחנה בפועל'] or None,
                                            exp_departure=d[
                                                              'תאריך וזמן יציאת רכבת מהתחנה מתוכנן'] or None if not stop_kind.is_dest else None,
                                            actual_departure=d[
                                                                 'תאריך וזמן יציאת רכבת מהתחנה בפועל'] or None if not stop_kind.is_dest else None,
                                            filename=base_xlname,
                                            line_number=rowx,
                                            valid=valid,
                                            invalid_reason=invalid_reason,
                                            index=int(d['מספר סידורי של התחנה']))
            except Exception as e:
                raise ValueError("Failed in row {} {}: {}".format(rowx, pprint.pformat(d), e))
                # else:
                # LOGGER.info("Skipped sample %s", pprint.pformat(d))
        prev_trip_num_date = cur_trip_num_date
    LOGGER.info("Created %s trips", len(created_ids))
    LOGGER.info("Start checking....")
    created_trips = data.models.Trip.objects.filter(id__in=created_ids)
    for idx, trip in enumerate(created_trips):
        trip.check_trip()
        if (idx + 1) % 100 == 0:
            LOGGER.info("checked %s / %s trips", idx + 1, len(created_trips))

    created_trips = data.models.Trip.objects.filter(id__in=created_ids)

    LOGGER.info("Creating routes")
    for trip in created_trips:
        trip.complete_trip()

    LOGGER.info("# of valid trips = %s", created_trips.filter(valid=True).count())
    LOGGER.info("# of invalid trips = %s", created_trips.filter(valid=False).count())

    invalid_summary = created_trips.filter(valid=False).values("invalid_reason").annotate(num=Count("id")).order_by()
    for line in invalid_summary:
        LOGGER.info("Reason: %s count = %s", line['invalid_reason'], line['num'])
