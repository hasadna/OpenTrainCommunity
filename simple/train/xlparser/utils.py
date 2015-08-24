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
        header = None
        good = 0
        bad = 0
        for rownum in xrange(sheet.nrows):
            values = sheet.row_values(rownum)
            clean_values = clean_row(rownum, values)
            if clean_values:
                if not header:
                    header = clean_values
                else:
                    assert len(header) == len(clean_values)
                    xl_row_to_csv(header, clean_values)
                    good+=1
            else:
                bad+=1

    print 'Bad rows: %s' % bad
    print 'Header row: %s' % 1 if header is not None else 0
    print 'Good rows: %s' % good
    print 'Wrote csv to {0}'.format(csvname)


def clean_row(row_num, values):
    empties = len([v for v in values[1:] if v is None or v == ''])
    if  len(values) - empties >= 4:
        return values[1:]
    return None

def xl_row_to_csv(header, values):
    return

