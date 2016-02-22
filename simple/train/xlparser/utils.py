#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import xlrd
import os
import datetime
import pytz
import logging


LOGGER = logging.getLogger(__name__)

ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')

VERSION = 2

class DtEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            if o.tzinfo != ISRAEL_TIMEZONE:
                o = o.astimezone(ISRAEL_TIMEZONE)
            return list(o.timetuple()[0:6])
        if isinstance(o, datetime.date):
            return list(o.timetuple()[0:6])
        return super().default(o)


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
    heb_header = [sheet.cell_value(3, colx) for colx in range(1, sheet.ncols)]
    txtname = os.path.splitext(xlname)[0] + '.txt'
    jsonname = os.path.splitext(xlname)[0] + '.json'
    with open(jsonname, 'w') as jsonfh, open(txtname, 'w') as txt:
        txt.write(json.dumps(heb_header))
        # this is 0 based, e.g. row #4 is row 5 in the excel (since excel sheet itself is 1 based)
        for rowx in range(4, sheet.nrows):
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
            txt.write(json.dumps(row, cls=DtEncoder))
            txt.write('\n')
            d = dict((HEADER_MAPPING[h][0],
                      HEADER_MAPPING[h][1](v)) for h, v in zip(heb_header,row))
            jsonfh.write(json.dumps(d, cls=DtEncoder))
            jsonfh.write("\n")
            if rowx % 20000 == 0:
                LOGGER.info('Completed %s/%s rows', rowx, sheet.nrows)
        LOGGER.info('Wrote {0}'.format(jsonfh.name))
        LOGGER.info('Wrote {0}'.format(txt.name))


def to_dt(dt):
    if not dt or dt == '':
        return None
    return dt


def to_d(dt):
    return dt.date()


def int_or_none(v):
    if v == '' or v is None:
        return None
    return int(v)


def identity(x):
    return x


def dt_to_csv(dt):
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()
    return ''


def to_bool(v):
    return bool(v)


HEADER_MAPPING = dict()
HEADER_MAPPING['תאריך נסיעת רכבת'] = ('train_date',to_d)
HEADER_MAPPING['מספר רכבת'] = ('train_num',int_or_none)
HEADER_MAPPING['רכבת מתוכננת/לא מתוכננת'] = ('is_planned_trip',identity)
HEADER_MAPPING['מספר תחנה'] = ('stop_id', int_or_none)
HEADER_MAPPING['תאור תחנה'] = ('stop_name', identity)
HEADER_MAPPING['מספר סידורי של התחנה'] = ('index', int_or_none)
HEADER_MAPPING['תאור קו נוסעים'] = ('route_name', identity)
HEADER_MAPPING['אופי התחנה'] = ('stop_kind', identity)
HEADER_MAPPING['האם תחנת עצירה מתוכננת'] = ('is_planned', to_bool)
HEADER_MAPPING['האם תחנת עצירה בפועל'] = ('is_stopped', to_bool)
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה מתוכנן'] = ('exp_departure', to_dt)
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה בפועל'] = ('actual_departure',to_dt)
HEADER_MAPPING['תאריך ושעת הגעה לתחנה מתוכנן'] = ('exp_arrival',to_dt)
HEADER_MAPPING['תאריך ושעת הגעה לתחנה בפועל'] = ('actual_arrival',to_dt)


if __name__ == '__main__':
    parse_xl(sys.argv[1])


def parse_json(filename, fromline, toline):
    with open(filename,'r') as fh:
        for idx, line in enumerate(fh):
            if fromline <= idx <= toline:
                print(json.dumps(json.loads(line), indent=4, sort_keys=True))



