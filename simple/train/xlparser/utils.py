#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xlrd
import unicodecsv
import os
import datetime
from django.utils import timezone

HEADER_MAPPING = dict()
HEADER_MAPPING['תאריך נסיעת רכבת'] = 'train_date'
HEADER_MAPPING['מספר רכבת'] = 'train_num'
HEADER_MAPPING['רכבת מתוכננת/לא מתוכננת'] = 'is_planned'
HEADER_MAPPING['מספר תחנה'] = 'stop_id'
HEADER_MAPPING['תאור תחנה'] = 'stop_name'
HEADER_MAPPING['מספר סידורי של התחנה'] = 'index'
HEADER_MAPPING['תאור קו נוסעים'] = 'route_nme'
HEADER_MAPPING['אופי התחנה'] = 'stop_kind'
HEADER_MAPPING['האם תחנת עצירה מתוכננת'] = 'is_planned'
HEADER_MAPPING['האם תחנת עצירה בפועל'] = 'is_stopped'
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה מתוכנן'] = 'exp_departure'
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה בפועל'] = 'actual_departure'
HEADER_MAPPING['תאריך ושעת הגעה לתחנה מתוכנן'] = 'exp_arrival'
HEADER_MAPPING['תאריך ושעת הגעה לתחנה בפועל'] = 'actual_arrival'


def parse_xl(xlname, csvname=None):
    wb = xlrd.open_workbook(xlname)
    sheet = wb.sheet_by_index(0)
    heb_header = [sheet.cell_value(3, colx) for colx in xrange(1, sheet.ncols)]
    header = [HEADER_MAPPING[h] for h in heb_header]

    for rowx in xrange(4, sheet.nrows):
        row = []
        for colx in xrange(1, sheet.ncols):
            cell_value = sheet.cell_value(rowx, colx)
            cell_type = sheet.cell_type(rowx, colx)
            if cell_type == xlrd.XL_CELL_DATE:
                dt_tuple = xlrd.xldate_as_tuple(cell_value, wb.datemode)
                dt = datetime.datetime(*dt_tuple)
                dt = timezone.get_default_timezone().localize(dt)
                row.append(dt)
            else:
                row.append(cell_value)
        xl_row_to_csv(dict(zip(header,row)))
        return


CSV_HEADER = ['train_num',
                'start_date',
                'trip_name',
                'index',
                'stop_id',
                'stop_name',
                'is_real_stop',
                'valid',
                'is_first',
                'is_last',
                'actual_arrival',
                'exp_arrival',
                'delay_arrival',
                'actual_departure',
                'exp_departure',
                'delay_departure',
                'data_file',
                'data_file_line',
                'data_file_link'
                ]


def xl_row_to_csv(row_dict):
    print row_dict


    output_dict = dict()
    for n in CSV_HEADER:
        output_dict[n] = None

