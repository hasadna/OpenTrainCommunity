#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import xlrd
import os
import csv
import datetime
import pytz
import logging


LOGGER = logging.getLogger(__name__)

ISRAEL_TIMEZONE = pytz.timezone('Asia/Jerusalem')


class DtEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            if o.tzinfo != ISRAEL_TIMEZONE:
                o = o.astimezone(ISRAEL_TIMEZONE)
            return list(o.timetuple()[0:6])
        return super().default(o)



def parse_xl(xlname):
    """
    :param xlname: xl file name
    :return: None
    creates xl file name and outputs two files, one is csv which we import,
    and the otherone is txt file which is text representation of the excel file
    used for the source ref in the browse app
    """
    base_xlname = os.path.basename(xlname)
    wb = xlrd.open_workbook(xlname)
    sheet = wb.sheet_by_index(0)
    heb_header = [sheet.cell_value(3, colx) for colx in range(1, sheet.ncols)]
    header = [HEADER_MAPPING[h] for h in heb_header]
    csvname = os.path.splitext(xlname)[0] + '.csv'
    txtname = os.path.splitext(xlname)[0] + '.txt'
    with open(csvname, 'w') as fh, open(txtname, 'w') as txt:
        wr = csv.DictWriter(fh, quoting=csv.QUOTE_ALL, fieldnames=CSV_HEADER)
        wr.writeheader()
        txt.write(json.dumps(heb_header))
        txt.write('\n')
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
            d = dict(zip(header, row))
            output_dict = xl_row_to_csv(d, base_xlname, rowx)
            txt.write(json.dumps(row, cls=DtEncoder))
            txt.write('\n')
            wr.writerow(output_dict)

            if rowx % 20000 == 0:
                LOGGER.info('Completed %s/%s rows', rowx, sheet.nrows)
        LOGGER.info('Wrote {0}'.format(fh.name))


HEADER_MAPPING = dict()
HEADER_MAPPING['תאריך נסיעת רכבת'] = 'train_date'
HEADER_MAPPING['מספר רכבת'] = 'train_num'
HEADER_MAPPING['רכבת מתוכננת/לא מתוכננת'] = 'is_planned'
HEADER_MAPPING['מספר תחנה'] = 'stop_id'
HEADER_MAPPING['תאור תחנה'] = 'stop_name'
HEADER_MAPPING['מספר סידורי של התחנה'] = 'index'
HEADER_MAPPING['תאור קו נוסעים'] = 'route_name'
HEADER_MAPPING['אופי התחנה'] = 'stop_kind'
HEADER_MAPPING['האם תחנת עצירה מתוכננת'] = 'is_planned'
HEADER_MAPPING['האם תחנת עצירה בפועל'] = 'is_stopped'
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה מתוכנן'] = 'exp_departure'
HEADER_MAPPING['תאריך ושעת יציאה מהתחנה בפועל'] = 'actual_departure'
HEADER_MAPPING['תאריך ושעת הגעה לתחנה מתוכנן'] = 'exp_arrival'
HEADER_MAPPING['תאריך ושעת הגעה לתחנה בפועל'] = 'actual_arrival'


def to_dt_str(dt,date_only=False):
    if not dt:
        return ''
    dt = datetime.datetime(*dt)
    ISRAEL_TIMEZONE.localize(dt)
    if not date_only:
        return dt.strftime('%H:%M:%S %d/%m/%Y')
    return dt.strftime('%d/%m/%Y')


def to_d_str(dt):
    return to_dt_str(dt, date_only=True)


def int_or_none(v):
    if v == '' or v is None:
        return ''
    return int(v)


HEADER_TO_STRING = dict()
HEADER_TO_STRING['תאריך נסיעת רכבת'] = to_d_str
HEADER_TO_STRING['מספר רכבת'] = int
HEADER_TO_STRING['רכבת מתוכננת/לא מתוכננת'] = str
HEADER_TO_STRING['מספר תחנה'] = int
HEADER_TO_STRING['תאור תחנה'] = str
HEADER_TO_STRING['מספר סידורי של התחנה'] = int
HEADER_TO_STRING['תאור קו נוסעים'] = str
HEADER_TO_STRING['אופי התחנה'] = str
HEADER_TO_STRING['האם תחנת עצירה מתוכננת'] = int_or_none
HEADER_TO_STRING['האם תחנת עצירה בפועל'] = int_or_none
HEADER_TO_STRING['תאריך ושעת יציאה מהתחנה מתוכנן'] = to_dt_str
HEADER_TO_STRING['תאריך ושעת יציאה מהתחנה בפועל'] = to_dt_str
HEADER_TO_STRING['תאריך ושעת הגעה לתחנה מתוכנן'] = to_dt_str
HEADER_TO_STRING['תאריך ושעת הגעה לתחנה בפועל'] = to_dt_str


STOP_KINDS = {
    'source_operation': 'מוצא תפעולי',
    'source_commercial': 'מוצא מסחרי',
    'source': 'מוצא',
    'middle': 'ביניים',
    'dest_operation': 'יעד תפעולי',
    'dest_commercial': 'יעד מסחרי',
    'dest': 'יעד'
}

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
              'data_file_link',
              # 'is_planned',  ## NEW
              # 'is_stopped'  ## NEW
              ]


def bool_to_csv(b):
    return '1' if b else '0'


def dt_to_csv(dt):
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()
    return ''


def diff_dt(actual, exp):
    if isinstance(actual, datetime.datetime) and isinstance(exp, datetime.datetime):
        return (actual - exp).total_seconds()
    return ''


def xl_row_to_csv(input_dict, filename, linenum):
    output_dict = dict()
    for n in CSV_HEADER:
        output_dict[n] = ''
    output_dict['train_num'] = int(input_dict['train_num'])
    output_dict['start_date'] = input_dict['train_date'].date().isoformat()
    output_dict['trip_name'] = '{0}_{1}'.format(output_dict['train_num'],
                                                output_dict['start_date'].replace('_', ''))  # is it necessary?
    output_dict['index'] = int(input_dict['index'])
    output_dict['stop_id'] = int(input_dict['stop_id'])
    output_dict['stop_name'] = input_dict['stop_name']
    output_dict['is_real_stop'] = bool_to_csv(input_dict['is_stopped'] and
                                              input_dict['stop_kind'] != STOP_KINDS['source_operation'])  ## CHANGED
    output_dict['valid'] = bool_to_csv(True)
    output_dict['is_first'] = bool_to_csv(input_dict['stop_kind']
                                          in (STOP_KINDS['source'], STOP_KINDS['source_commercial']))
    output_dict['is_last'] = bool_to_csv(input_dict['stop_kind'] == STOP_KINDS['dest'])
    for f in ['actual_arrival', 'actual_departure', 'exp_arrival', 'exp_departure']:
        output_dict[f] = dt_to_csv(input_dict[f])
    output_dict['delay_arrival'] = diff_dt(input_dict['actual_arrival'], input_dict['exp_arrival'])
    output_dict['delay_departure'] = diff_dt(input_dict['actual_departure'], input_dict['exp_departure'])
    # output_dict['is_planned'] = bool_to_csv(input_dict['is_planned'])  ### NEW
    # output_dict['is_stopped'] = bool_to_csv(input_dict['is_stopped'])  ### NEW
    # Suggestion - to consider the cases in which a train skipped a station (it's severe) but not to consider the cases
    # in which a train added an unplanned station (very rare and not severe)
    # eran: this is great idea, for now I don't want to add new fields to the csv, until we change the csv code
    # anyway, we should maybe consider write all this import from scratch...
    output_dict['data_file'] = filename
    output_dict['data_file_line'] = linenum
    return output_dict


if __name__ == '__main__':
    import sys

    parse_xl(sys.argv[1])
