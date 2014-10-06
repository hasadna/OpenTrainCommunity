import codecs
import re
import datetime
import argparse
import pytz
import os
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

DELAY_THRESHOLD = 60 * 90
ONE_DAY = datetime.timedelta(hours=24)

ERROR_NO_STOPS='ERROR_NO_STOPS'
ERROR_EXP_ARRIVAL_NON_NONE='ERROR_EXP_ARRIVAL_NON_NONE'
ERROR_ACTUAL_ARRIVAL_NON_NONE='ERROR_ACTUAL_ARRIVAL_NON_NONE'
ERROR_EXP_DEPARTURE_NON_NONE='ERROR_EXP_DEPARTURE_NON_NONE'
ERROR_ACTUAL_DEPARTURE_NON_NONE='ERROR_ACTUAL_DEPARTURE_NON_NONE'
ERROR_EXP_ARRIVAL_NONE='ERROR_EXP_ARRIVAL_NONE'
ERROR_EXP_DEPARTURE_NONE='ERROR_EXP_DEPARTURE_NONE'
ERROR_ARRIVE_DELAY_TOO_LONG='ERROR_ARRIVE_DELAY_TOO_LONG'
ERROR_DEPARTURE_DELAY_TOO_LONG='ERROR_DEPARTURE_DELAY_TOO_LONG'

class CheckException(Exception):
    def __init__(self,code,details=None):
        if details:
            text = '%s: %s' % (code,details)
        else:
            text = code
        self.code = code
        self.details = details
        super(CheckException,self).__init__(text)


class Trip(object):
    def __init__(self, stops):
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
        except CheckException, e:
            self.error = e

    def do_check(self):
        if not self.stops:
            raise CheckException(ERROR_NO_STOPS)

        if self.stops[0].exp_arrival is not None:
            raise CheckException(ERROR_EXP_ARRIVAL_NON_NONE)

        if self.stops[0].actual_arrival is not None:
            raise CheckException(ERROR_ACTUAL_ARRIVAL_NON_NONE)

        if self.stops[-1].exp_departure is not None:
            raise CheckException(ERROR_EXP_DEPARTURE_NON_NONE)

        if self.stops[-1].actual_departure is not None:
            raise CheckException(ERROR_ACTUAL_DEPARTURE_NON_NONE)

        for idx, stop in enumerate(self.stops[1:]):
            if stop.exp_arrival is None:
                raise CheckException(ERROR_EXP_ARRIVAL_NONE,'stop is %s' % stop)
        for idx, stop in enumerate(self.stops[0:-1]):
            if stop.exp_departure is None:
                raise CheckException(ERROR_EXP_DEPARTURE_NONE,'stop is %s' % stop)

        for stop in self.stops:
            delay_arrive = stop.get_delay_arrival()
            if delay_arrive is not None and abs(
                delay_arrive) > DELAY_THRESHOLD:
                raise CheckException(ERROR_ARRIVE_DELAY_TOO_LONG,'stop is %s' % unicode(stop))
            delay_departure = stop.get_delay_departure()
            if delay_departure is not None and abs(
                delay_departure) > DELAY_THRESHOLD:
                raise CheckException(ERROR_DEPARTURE_DELAY_TOO_LONG,'stop is %s' % unicode(stop))


class StopLine(object):
    def parse_time(self, t):
        t = int(t)
        if t == 0:
            return None
        m = t % 100
        h = (t - t % 100) / 100
        dt = datetime.datetime(year=self.date.year, month=self.date.month, day=self.date.day) + datetime.timedelta(
            hours=h, minutes=m)
        return ISRAEL_TZ.localize(dt)

    def build_times(self, aa, ea, ad, ed):
        self.actual_arrival = self.parse_time(aa)
        self.exp_arrival = self.parse_time(ea)
        self.actual_departure = self.parse_time(ad)
        self.exp_departure = self.parse_time(ed)
        # the date is according to the exp_arrival,
        # so if it before 24 and other are low, we need to offset them in 24 hours
        if self.exp_arrival and self.exp_arrival.hour >= 22:
            if self.actual_arrival and self.actual_arrival.hour < 3:
                self.actual_arrival += ONE_DAY
            if self.exp_departure and self.exp_departure.hour < 3:
                self.exp_departure += ONE_DAY
            if self.actual_departure and self.actual_departure.hour < 3:
                self.actual_departure += ONE_DAY
        # the other case, if if exp_arrival is "tomorrow" and we have something from today
        elif self.exp_arrival and self.exp_arrival.hour <= 3:
            if self.actual_arrival and self.actual_arrival.hour >= 22:
                self.actual_arrival -= ONE_DAY
            if self.exp_departure and self.exp_departure.hour >= 22:
                self.exp_departure -= ONE_DAY
            if self.actual_departure and self.actual_departure.hour >= 22:
                self.actual_departure -= ONE_DAY




    def get_delay_arrival(self):
        if self.exp_arrival is None or self.actual_arrival is None:
            return None
        return (self.actual_arrival - self.exp_arrival).total_seconds()

    def get_delay_departure(self):
        if self.exp_departure is None or self.actual_departure is None:
            return None
        return (self.actual_departure - self.exp_departure).total_seconds()


    def print_time(self, dt):
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
                if (1 + idx) % 10000 == 0:
                    print 'parsed %d lines' % (idx + 1)

    def build_trips(self):
        stops_by_trip_num = defaultdict(list)
        for trip in self.stop_lines:
            stops_by_trip_num[trip.train_num].append(trip)

        for trip_num, trips in stops_by_trip_num.iteritems():
            self.split_trips(trip_num, trips)

    def make_log_dir(self):
        if not os.path.exists('log'):
            os.mkdir('log')

    def print_trips_status(self):
        invalid_trips = [trip for trip in self.trips if not trip.is_valid]
        print 'Total trips: %d' % len(self.trips)
        print 'Invalid trips: %d' % len(invalid_trips)
        count_by_code = defaultdict(int)
        for invalid_trip in invalid_trips:
            count_by_code[invalid_trip.error.code]+=1
        for code,code_count in count_by_code.iteritems():
            print '    %s: %s' % (code,code_count)

        invalid_file = 'log/invalid.txt'
        self.make_log_dir()
        with codecs.open(invalid_file, 'w', 'utf-8') as invalid_fh:
            for invalid_trip in invalid_trips:
                invalid_fh.write('%s: %s\n' % (unicode(invalid_trip), unicode(invalid_trip.error)))
        print 'Invalid details written to %s' % invalid_file


    def split_trips(self, trip_num, stops):
        cur_stops = []
        for idx, stop in enumerate(stops):
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
            sl.line = idx + 1  # make it base 1 now, like file editors
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
        # self.dump()


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
