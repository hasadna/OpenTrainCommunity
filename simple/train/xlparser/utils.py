import xlrd
import unicodecsv
import os

def parse_xl(xlname, csvname=None):
    if csvname is None:
        csvname = os.path.splitext(xlname)[0] + '.csv'
    with open(csvname,'w') as fh:
        wr = unicodecsv.writer(fh, quoting=unicodecsv.QUOTE_ALL)
        wb = xlrd.open_workbook(xlname)
        sheet = wb.sheet_by_index(0)
        invalid = []
        for rownum in xrange(sheet.nrows):
            values = sheet.row_values(rownum)
            clean_values = clean_row(rownum, values)
            if clean_values is not None:
                wr.writerow(clean_values)
            else:
                invalid.append(rownum)
    print 'Invalid rows: %s' % invalid
    print 'Wrote csv to {0}'.format(csvname)

def clean_row(row_num, values):
    empties = len([v for v in values[1:] if v is None or v == ''])
    if  len(values) - empties >= 4:
        return values[1:]
    return None


