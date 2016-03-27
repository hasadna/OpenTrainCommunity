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


def xl2text(xlname):
    """
    :param xlname: xl file name
    converts the xl to text for displaying
    """
    base_xlname = os.path.basename(xlname)
    wb = xlrd.open_workbook(xlname)
    sheet = wb.sheet_by_index(0)
    txtname = os.path.splitext(xlname)[0] + '.txt'
    with open(txtname,"w") as txt:
        for rowx in range(1, sheet.nrows):
            row = []
            for colx in range(1, sheet.ncols):
                cell_value = sheet.cell_value(rowx, colx)
                cell_type = sheet.cell_type(rowx, colx)
                if cell_type == xlrd.XL_CELL_DATE:
                    dt_tuple = xlrd.xldate_as_tuple(cell_value, wb.datemode)
                    dt = datetime.datetime(*dt_tuple)
                    dt = ISRAEL_TIMEZONE.localize(dt)
                    row.append(dt.isoformat())
                else:
                    row.append(str(cell_value))
            txt.write(",".join(row))
            txt.write('\n')
            if rowx % 20000 == 0:
                LOGGER.info('Completed %s/%s rows', rowx, sheet.nrows)
        LOGGER.info('Wrote {0}'.format(txt.name))

