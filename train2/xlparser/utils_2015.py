#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import pprint
from collections import namedtuple

import pytz
import xlrd
from django.db import transaction
from django.db.models import Count

import data.importer
import data.models

LOGGER = logging.getLogger(__name__)

ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')

TripNumDate = namedtuple('TripNumDate', ('num', 'date'))

StopKind = namedtuple('StopKind', ['is_commercial', 'is_source', 'is_middle', 'is_dest'])

STOP_KIND = {
    'יעד': StopKind(True, False, False, True),
    'יעד מסחרי': StopKind(True, False, False, True),
    'יעד תפעולי': StopKind(False, False, False, True),
    'ביניים': StopKind(True, False, True, False),
    'מוצא': StopKind(True, True, False, False),
    'מוצא מסחרי': StopKind(True, True, False, False),
    'מוצא תפעולי': StopKind(False, True, False, False),
}

STOP_IS_COMMERCIAL = {
    'מסחרית': True,
    'לא מסחרית': False,
}


def is1(val):
    if not val:
        return False
    return int(val) == 1


def read_sheet(wb, sheet_idx, *, heb_header, base_xlname, global_data):
    LOGGER.info("Starting sheet %d", sheet_idx)
    sheet = wb.sheet_by_index(sheet_idx)
    first_row = 2 if sheet_idx == 0 else 0
    for rowx in range(first_row, sheet.nrows):
        row = []
        if rowx % 1000 == 0:
            LOGGER.info("%s rows / %s", rowx, sheet.nrows)
        for colx in range(1, sheet.ncols):
            cell_value = sheet.cell_value(rowx, colx)
            cell_type = sheet.cell_type(rowx, colx)
            if cell_type == xlrd.XL_CELL_DATE:
                dt_tuple = xlrd.xldate_as_tuple(cell_value, wb.datemode)
                dt = datetime.datetime(*dt_tuple)
                dt = ISRAEL_TIMEZONE.localize(dt)
                row.append(dt)
            else:
                row.append(cell_value)
        d = dict(zip(heb_header, row))
        cur_trip_num_date = TripNumDate(num=int(d['מספר רכבת']), date=d['תאריך נסיעת רכבת'].date())
        if cur_trip_num_date != global_data.prev_trip_num_date:
            global_data.cur_trip = data.importer.create_trip(train_num=cur_trip_num_date.num,
                                                 date=cur_trip_num_date.date)
            global_data.created_ids.append(global_data.cur_trip.id)
        # we skip all sample whose stops are no commercial or if they are not stopped
        # or if this is non commerical source/dest
        try:
            if d['אופי התחנה']:  # might be empty string
                stop_kind = STOP_KIND[d['אופי התחנה']]
                is_commercial_stop = STOP_IS_COMMERCIAL[d['האם תחנה מסחרית']] and stop_kind.is_commercial
                is_stopped = is1(d['האם תחנת עצירה בפועל'])

                is_planned_stop = is1(d['האם תחנת עצירה מתוכננת'])
            else:
                is_commercial_stop = False

            valid = True
            invalid_reason = None

            if is_commercial_stop:
                if is_planned_stop != is_stopped:
                    valid = False
                    invalid_reason = 'sample has different planned and stopped'
        except Exception as e:
            raise ValueError("Failed in row {} {}: {}".format(rowx, pprint.pformat(d), e))

        if is_commercial_stop and is_stopped:
            try:
                data.importer.create_sample(trip=global_data.cur_trip,
                                            is_source=stop_kind.is_source,
                                            is_dest=stop_kind.is_dest,
                                            gtfs_stop_id=int(d['מספר תחנה']),
                                            gtfs_stop_name=d['תאור תחנה'],
                                            exp_arrival=d['תאריך וזמן הגעת רכבת לתחנה מתוכנן'] or None,
                                            actual_arrival=d['תאריך וזמן הגעת רכבת לתחנה בפועל'] or None,
                                            exp_departure=d[
                                                              'תאריך וזמן יציאת רכבת מהתחנה מתוכנן'] or None if not stop_kind.is_dest else None,
                                            actual_departure=d[
                                                                 'תאריך וזמן יציאת רכבת מהתחנה בפועל'] or None if not stop_kind.is_dest else None,
                                            filename=base_xlname,
                                            line_number=rowx,
                                            sheet_idx=sheet_idx,
                                            valid=valid,
                                            invalid_reason=invalid_reason,
                                            index=int(d['מספר סידורי של התחנה']))
            except Exception as e:
                raise ValueError("Failed in row {} {}: {}".format(rowx, pprint.pformat(d), e))
                # else:
                # LOGGER.info("Skipped sample %s", pprint.pformat(d))
        global_data.prev_trip_num_date = cur_trip_num_date


class GlobalData:
    def __init__(self, *, prev_trip_num_date, created_ids):
        self.prev_trip_num_date = prev_trip_num_date
        self.created_ids = created_ids
        self.cur_trip = None


@transaction.atomic
def parse_xl(xlname):
    """
    :param xlname: xl file name
    :return: None
    creates xl file name and outputs two files, one is csv which we import,
    and the other one is txt file which is text representation of the excel file
    used for the source ref in the browse app
    """
    base_xlname = os.path.basename(xlname)
    wb = xlrd.open_workbook(xlname)
    sheet0 = wb.sheet_by_index(0)
    heb_header = [sheet0.cell_value(1, colx) for colx in range(1, sheet0.ncols)]
    prev_trip_num_date = TripNumDate(num=None, date=None)
    created_ids = []
    global_data = GlobalData(
        created_ids=created_ids,
        prev_trip_num_date=prev_trip_num_date,
    )
    nsheets = wb.nsheets
    for sheet_idx in range(0, nsheets):
        read_sheet(wb, sheet_idx,
                   heb_header=heb_header,
                   base_xlname=base_xlname,
                   global_data=global_data)

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
