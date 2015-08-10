import StringIO
import xlrd
import unicodecsv

def parse_xl(fname):
    si = StringIO.StringIO()
    wr = unicodecsv.writer(si,quoting=unicodecsv.QUOTE_ALL)
    wb = xlrd.open_workbook(fname)
    sheet = wb.sheet_by_index(0)
    for rownum in xrange(sheet.nrows):
        values = sheet.row_values(rownum)
        wr.writerow(values)
    return si.getvalue().strip('\r\n')


