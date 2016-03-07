#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from collections import defaultdict, namedtuple

import xlrd
import os
import datetime
import pytz
import logging
import pprint

from django.db import transaction

from data import importer

LOGGER = logging.getLogger(__name__)

ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')

TripNumDate = namedtuple('TripNumDate', ('num', 'date'))

STOP_KIND = {
    'יעד': (False, False, True),
    'יעד מסחרי': (False, False, True),
    'יעד תפעולי': (False, False, True),
    'ביניים': (False, True, False),
    'מוצא': (True, False, False),
    'מוצא מסחרי': (True, False, False),
    'מוצא תפעולי': (True, False, False),
}


def is1(val):
    if not val:
        return False
    return int(val) == 1

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
    sheet = wb.sheet_by_index(0)
    heb_header = [sheet.cell_value(1, colx) for colx in range(1, sheet.ncols)]
    prev_trip_num_date = TripNumDate(num=None, date=None)
    for rowx in range(2, sheet.nrows):
        row = []
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
        cur_trip_num_date = TripNumDate(num=int(d['מספר רכבת']), date=d['תאריך נסיעת רכבת'])
        if cur_trip_num_date != prev_trip_num_date:
            cur_trip = importer.create_trip(train_num=cur_trip_num_date.num,
                                            date=cur_trip_num_date.date)
        is_commercial_stop = d['האם תחנה מסחרית'] not in ['לא מסחרית']
        is_stop = is1(d['האם תחנת עצירה בפועל'])
        is_source = STOP_KIND[d['אופי התחנה']][0]
        is_middle = STOP_KIND[d['אופי התחנה']][1]
        is_dest = STOP_KIND[d['אופי התחנה']][2]

        if is_commercial_stop and is_stop:
            try:
                importer.create_sample(trip=cur_trip,
                                       is_source=is_source,
                                       is_dest=is_dest,
                                       gtfs_stop_id=int(d['מספר תחנה']),
                                       exp_arrival=d['תאריך וזמן הגעת רכבת לתחנה מתוכנן'] or None,
                                       actual_arrival=d['תאריך וזמן הגעת רכבת לתחנה בפועל'] or None,
                                       exp_departure=d['תאריך וזמן יציאת רכבת מהתחנה מתוכנן'] or None if not is_dest else None,
                                       actual_departure=d['תאריך וזמן יציאת רכבת מהתחנה בפועל'] or None if not is_dest else None,
                                       filename=base_xlname,
                                       line_number=rowx,
                                       index=int(d['מספר סידורי של התחנה']))
            except Exception as e:
                raise ValueError("Failed in row {} {}: {}".format(rowx, pprint.pformat(d), e))
        #else:
            #LOGGER.info("Skipped sample %s", pprint.pformat(d))
        prev_trip_num_date = cur_trip_num_date
