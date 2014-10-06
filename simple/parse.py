import codecs
import re
import datetime
import argparse
import pytz
import itertools
from collections import defaultdict


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

DELAY_THRESHOLD = 60*90

class Trip(object):
    def __init__(self,stops):
        self.train_num = stops[0].train_num
        self.stops = stops
        self.is_valid = False
        self.error = None
        self.check()

    def __unicode__(self):
        return '%s: %s - %s' % (self.train_num, unicode(self.stops[0]), unicode(self.stops[-1]))

    def check(self):
        try:
            self.do_check()
            self.is_valid = True
        except Exception, e:
            self.error = unicode(e)

    def do_check(self):
        assert self.stops, 'no stops'
        assert self.stops[0].exp_arrival is None,'exp arrival of 0 is not None'
        assert self.stops[0].actual_arrival is None,'actual arrival of 0 is not None'
        assert self.stops[-1].exp_departure is None,'exp departure of -1 is not None'
        assert self.stops[-1].actual_departure is None,'actual departure of -1 is not None'

        for idx,stop in enumerate(self.stops[1:]):
            assert stop.exp_arrival is not None,'exp arrival of %d is None' % idx
        for idx,stop in enumerate(self.stops[0:-1]):
            assert stop.exp_departure is not None,'exp departure of %d is None' % idx

        for stop in self.stops:
            delay_arrive = stop.get_delay_arrival()
            assert delay_arrive is None or abs(delay_arrive) < DELAY_THRESHOLD,'delay_arrive too big: %d' % delay_arrive
            delay_departure = stop.get_delay_departure()
            assert delay_departure is None or abs(delay_departure) < DELAY_THRESHOLD,'delay_departure too big: %d' % delay_departure
        
                


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

    def get_delay_arrival(self):
        if self.exp_arrival is None or self.actual_arrival is None:
            return None
        return (self.actual_arrival - self.exp_arrival).total_seconds()
    
    def get_delay_departure(self):
        if self.exp_departure is None or self.actual_departure is None:
            return None
        return (self.actual_departure - self.exp_departure).total_seconds()
    
    
    

    def print_time(self,dt):
        if dt is not None:
            return dt.strftime('%H:%M')
        else:
            return "-----"

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

    def build_trips(self):
        stops_by_trip_num = defaultdict(list)
        for trip in self.stop_lines:
            stops_by_trip_num[trip.train_num].append(trip)

        for trip_num,trips in stops_by_trip_num.iteritems():
            self.split_trips(trip_num,trips)

    def print_trips_status(self):
        invalid_trips = [trip for trip in self.trips if not trip.is_valid]
        print 'Total trips: %d' % len(self.trips)
        print 'Invalid trips: %d' % len(invalid_trips)
        with codecs.open('invalid.txt','w','utf-8') as invalid_fh:
            for invalid_trip in invalid_trips:
                invalid_fh.write('%s: %s\n' % (unicode(invalid_trip),invalid_trip.error))

    def split_trips(self,trip_num,stops):
        cur_stops = []
        for idx,stop in enumerate(stops):
            if stop.exp_arrival is None:
                if cur_stops:
                    trip = Trip(cur_stops)
                    self.trips.append(trip)
                    cur_stops = []
            cur_stops.append(stop)
        # build the left-overs
        if cur_stops:
            trip = Trip(cur_stops)
            self.trips.append(trip)

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
            is_real = stop_id in REAL_STOP_IDS

            sl = StopLine()
            sl.date = self._parse_date(gd['date'])
            sl.train_num = gd['train_num']
            sl.stop_id = stop_id
            sl.stop_name = gd['raw_stop_name'].strip()
            sl.file = self.ifile
            sl.line = idx + 1 # make it base 1 now, like file editors
            sl.is_real = is_real
            sl.build_times(gd['actual_arrival'],
                           gd['exp_arrival'],
                           gd['actual_departure'],
                           gd['exp_departure'])

            self.stop_lines.append(sl)
        else:
            raise Exception('Illegal line %d at %s' % (idx, self.ifile))

    def main(self):
        self.parse()
        self.build_trips()
        self.print_trips_status()
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
