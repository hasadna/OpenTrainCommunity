import codecs
import re
import datetime
import argparse

LINE_RE = re.compile(r'^\s*' +
                     r'(?P<date>\d+)\s+"' +
                     r'(?P<train_num>\d+)"\s+' +
                     r'(?P<exp_arrival>\d+)\s+' +
                     r'(?P<actual_arrival>\d+)\s+' +
                     r'(?P<exp_departure>\d+)\s+' +
                     r'(?P<actual_departure>\d+)\s+' +
                     r'(?P<raw_stop_id>\d+)\s+' +
                     r'"(?P<raw_stop_name>.*)"\s*$')


class StopLine(object):
    def parse_time(self,t):
        h = t % 100
        m = (t - t % 100) / 100
        #assert 0 <= h <= 23
        #assert 0 <= m <= 59
        return self.date

    def build_times(self,aa,ea,ad,ed):
        self.actual_arrival = self.parse_time(aa)
        self.exp_arrival = self.parse_time(ea)
        self.actual_departure = self.parse_time(ad)
        self.exp_departure = self.parse_time(ed)
    def __unicode__(self):
        return '%5d %4d %25s A=%5s(%5s) D=%5s(%5s)' % (self.line,
                                                       self.stop_id,
                                                       self.stop_name,
                                                       self.actual_arrival,
                                                       self.exp_arrival,
                                                       self.actual_departure,
                                                       self.exp_departure)


class TrainParser():
    def __init__(self, input, output, append):
        self.ifile = input
        self.append = append
        self.ofile = output
        self.stop_lines = []

    def parse(self):
        with codecs.open(self.ifile, encoding="windows-1255") as ifh:
            for idx, line in enumerate(ifh):
                self.parse_line(idx, line)

    def dump(self):
        for line in self.stop_lines:
            try:
                print unicode(line)
            except Exception, e:
                import pdb

                pdb.set_trace()

    def _parse_date(self, date):
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        return datetime.date(year=year, month=month, day=day)


    def parse_line(self, idx, line):
        m = LINE_RE.match(line)
        if m:
            td = StopLine()
            gd = m.groupdict()
            td.date = self._parse_date(gd['date'])
            td.train_num = gd['train_num']
            td.stop_id = int(gd['raw_stop_id'])
            td.stop_name = gd['raw_stop_name'].strip()
            td.file = self.ifile
            td.line = idx
            td.build_times(gd['actual_arrival'],
                           gd['exp_arrival'],
                           gd['actual_departure'],
                           gd['exp_departure'])

            # if td.raw_stop_id in stop_ids:
            # td.stop_id = td.raw_stop_id
            self.stop_lines.append(td)
            else:
            raise Exception('Illegal line %d at %s' % (idx, fname))


def main():
    parser = argparse.ArgumentParser('parser')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=False)
    parser.add_argument('--append', required=False, default=True, action='store_true')
    ns = parser.parse_args()
    tp = TrainParser(**vars(ns))
    tp.parse()
    tp.dump()


if __name__ == '__main__':
    main()
