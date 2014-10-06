import codecs
import re
import datetime
import argparse
import pytz
import itertools

ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')
LONG_AGO = ISRAEL_TZ.localize(datetime.datetime.fromtimestamp(0))

LINE_RE = re.compile(r'^\s*' +
                     r'(?P<date>\d+)\s+"' +
                     r'(?P<train_num>\d+)"\s+' +
                     r'(?P<exp_arrival>\d+)\s+' +
                     r'(?P<actual_arrival>\d+)\s+' +
                     r'(?P<exp_departure>\d+)\s+' +
                     r'(?P<actual_departure>\d+)\s+' +
                     r'(?P<raw_stop_id>\d+)\s+' +
                     r'"(?P<raw_stop_name>.*)"\s*$')

REAL_STOP_IDS = [8550, 800, 6700, 7300, 8700, 1500, 4690, 4600, 3400, 4640, 4680, 4170, 8600, 5410, 400, 6300, 9600,
                 2300, 5150, 5900, 7500, 9200, 8800, 9800, 1220, 4900, 9000, 2200, 7320, 3700, 5800, 5300, 2820, 2100,
                 3300, 9100, 2500, 3500, 4660, 3100, 300, 4250, 6500, 700, 1300, 4800, 1600, 5000, 2800, 3600, 4100,
                 5010, 5200, 7000]


class Trip(object):
    def __init__(self,stops):
        self.stops = stops
        self.is_valid = False
        self.error = None
        self.fix_split()
        self.check()

    def is_split(self):
        before_24 = False
        after_0 = False
        for stop in self.stops:
            if stop.exp_arrival and stop.exp_arrival.hour >= 22:
                before_24 = True
            if stop.exp_arrival and stop.exp_arrival.hour <= 2:
                after_0 = True
        return before_24 and after_0

    def fix_split(self):
        if self.is_split():
            for stop in self.stops:
                if stop.exp_arrival and stop.exp_arrival.hour < 12:
                    stop.exp_arrival += datetime.timedelta(hours=24)
                if stop.exp_departure and stop.exp_departure.hour < 12:
                    stop.exp_departure += datetime.timedelta(hours=24)
                if stop.actual_arrival and stop.actual_arrival.hour < 12:
                    stop.actual_arrival += datetime.timedelta(hours=24)
                if stop.actual_departure and stop.actual_departure.hour < 12:
                    stop.actual_departure += datetime.timedelta(hours=24)

            self.stops.sort(key=lambda x : x.exp_arrival or LONG_AGO)

    def check(self):
        try:
            self.do_check()
            self.is_valid = True
        except Exception,e:
            self.error = unicode(e)



    def do_check(self):
        assert self.stops,'no stops'
        assert self.stops[0].exp_arrival is None,'exp arrival of 0 is not None'
        assert self.stops[0].actual_arrival is None,'actual arrival of 0 is not None'
        assert self.stops[-1].exp_departure is None,'exp departure of -1 is not None'
        assert self.stops[-1].actual_departure is None,'actual departure of -1 is not None'

        for idx,stop in enumerate(self.stops[1:]):
            assert stop.exp_arrival is not None,'exp arrival of %d is None' % idx
        for idx,stop in enumerate(self.stops[0:-1]):
            assert stop.exp_departure is not None,'exp departure of %d is None' % idx




class StopLine(object):
    def parse_time(self, t):
        t = int(t)
        if t == 0:
            return None
        m = t % 100
        h = (t - t % 100) / 100
        dt = datetime.datetime(year=self.date.year,month=self.date.month,day=self.date.day) + datetime.timedelta(hours=h, minutes=m)
        return ISRAEL_TZ.localize(dt)

    def build_times(self, aa, ea, ad, ed):
        self.actual_arrival = self.parse_time(aa)
        self.exp_arrival = self.parse_time(ea)
        self.actual_departure = self.parse_time(ad)
        self.exp_departure = self.parse_time(ed)

    def print_time(self,dt):
        return dt.strftime('%H:%M')

    def __unicode__(self):
        return '%5d %4d %25s A=%5s(%5s) D=%5s(%5s)' % (self.line,
                                                       self.stop_id,
                                                       self.stop_name,
                                                       self.print_time(self.actual_arrival),
                                                       self.print_time(self.exp_arrival),
                                                       self.print_time(self.actual_departure),
                                                       self.print_time(self.exp_departure))


class TrainParser():
    def __init__(self, input, output, append):
        self.ifile = input
        self.append = append
        self.ofile = output
        self.stop_lines = []
        self.trips = []

    def parse(self):
        with codecs.open(self.ifile, encoding="windows-1255") as ifh:
            for idx, line in enumerate(ifh):
                self.parse_line(idx, line)
                if (1+idx) % 10000 == 0:
                    print 'parsed %d lines' % (idx+1)

    def collect_trips(self):
        group_res = itertools.groupby(self.stop_lines,key=lambda x : (x.date,x.train_num))
        for (date,train_num),stops_iter in group_res:
            trip  = Trip(list(stops_iter))
            if trip.is_valid:
                self.trips.append(trip)
            else:
                print 'Invalid trip: %s %s' % (unicode(trip),trip.error)


    def dump(self):
        for line in self.stop_lines:
            print unicode(line)

    def _parse_date(self, date):
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        return datetime.date(year=year, month=month, day=day)

    def parse_line(self, idx, line):
        m = LINE_RE.match(line)
        if m:
            gd = m.groupdict()
            stop_id = int(gd['raw_stop_id'])
            if stop_id not in REAL_STOP_IDS:
                return
            sl = StopLine()
            sl.date = self._parse_date(gd['date'])
            sl.train_num = gd['train_num']
            sl.stop_id = stop_id
            sl.stop_name = gd['raw_stop_name'].strip()
            sl.file = self.ifile
            sl.line = idx
            sl.build_times(gd['actual_arrival'],
                           gd['exp_arrival'],
                           gd['actual_departure'],
                           gd['exp_departure'])

            self.stop_lines.append(sl)
        else:
            raise Exception('Illegal line %d at %s' % (idx, self.ifile))

    def main(self):
        self.parse()
        self.collect_trips()
        #self.dump()


def main():
    parser = argparse.ArgumentParser('parser')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=False)
    parser.add_argument('--append', required=False, default=True, action='store_true')
    ns = parser.parse_args()
    tp = TrainParser(**vars(ns))
    tp.main()



if __name__ == '__main__':
    main()
