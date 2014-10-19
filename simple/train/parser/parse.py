import codecs
import re
import datetime
import argparse
import pytz
import os
from collections import defaultdict
import stops_utils

ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')
LONG_AGO = ISRAEL_TZ.localize(datetime.datetime.fromtimestamp(0))
MAX_GAP = 60 * 120  # 120 minutes
DELAY_THRESHOLD = 60 * 120  # 120 minutes
LINE_RE = re.compile(r'^\s*' +
                     r'(?P<date>\d+)\s+"' +
                     r'(?P<train_num>\d+)"\s+' +
                     r'(?P<exp_arrival>\d+)\s+' +
                     r'(?P<actual_arrival>\d+)\s+' +
                     r'(?P<exp_departure>\d+)\s+' +
                     r'(?P<actual_departure>\d+)\s+' +
                     r'(?P<raw_stop_id>\d+)\s+' +
                     r'"(?P<raw_stop_name>.*)"\s*$')

ONE_DAY = datetime.timedelta(hours=24)

ERROR_NO_STOPS = 'ERROR_NO_STOPS'
ERROR_EXP_ARRIVAL_NON_NONE = 'ERROR_EXP_ARRIVAL_NON_NONE'
ERROR_ACTUAL_ARRIVAL_NON_NONE = 'ERROR_ACTUAL_ARRIVAL_NON_NONE'
ERROR_EXP_DEPARTURE_NON_NONE = 'ERROR_EXP_DEPARTURE_NON_NONE'
ERROR_ACTUAL_DEPARTURE_NON_NONE = 'ERROR_ACTUAL_DEPARTURE_NON_NONE'
ERROR_EXP_ARRIVAL_NONE = 'ERROR_EXP_ARRIVAL_NONE'
ERROR_EXP_DEPARTURE_NONE = 'ERROR_EXP_DEPARTURE_NONE'
ERROR_ARRIVE_DELAY_TOO_LONG = 'ERROR_ARRIVE_DELAY_TOO_LONG'
ERROR_DEPARTURE_DELAY_TOO_LONG = 'ERROR_DEPARTURE_DELAY_TOO_LONG'
ERROR_GAP_TOO_LONG = 'ERROR_GAP_TOO_LONG'
ERROR_NEGATIVE_GAP = 'ERROR_NEGATIVE_GAP'
ERROR_DECR_CSV = 'ERROR_DECR_CSV'
ERROR_MISSING_SAMPLE = 'ERROR_MISSING_SAMPLE'
ERROR_DUPLICATE_NUM_DATE = 'ERROR_DUPLICATE_NUM_DATE'

class CheckException(Exception):
    def __init__(self, code, details=None):
        if details:
            text = '%s: %s' % (code, details)
        else:
            text = code
        self.code = code
        self.details = details
        super(CheckException, self).__init__(text)


class Trip(object):
    def __init__(self, stops):
        self.train_num = stops[0].train_num
        self.stops = stops
        self.is_valid = False
        self.error = None
        self.check()
        self.is_midnight = self.check_is_midnight()


    def print_full(self):
        print self.unicode_full()

    def unicode_full(self):
        res = []
        for idx, stop in enumerate(self.stops):
            res.append('%2d %s' % (idx, stop))
        return '\n'.join(res)

    def get_start_date(self):
        """
        return the date of the first exp_arrival
        """
        for stop in self.stops:
            if stop.exp_arrival:
                return stop.exp_arrival.date()

    def __unicode__(self):
        return 'Num %s%s in %s from %s to %s' % (self.stops[0].train_num,
                                                 ' [MID]' if self.is_midnight else '',
                                                 self.get_start_date(),
                                                 self.stops[0].stop_name,
                                                 self.stops[-1].stop_name)


    def check_is_midnight(self):
        attrs = ['actual_arrival', 'exp_arrival', 'actual_departure', 'exp_departure']
        before_midnight = False
        after_midnight = False
        for stop in self.stops:
            for attr in attrs:
                t = getattr(stop, attr)
                if t and t.hour >= 21:
                    before_midnight = True
                if t and t.hour <= 3:
                    after_midnight = True
                if before_midnight and after_midnight:
                    return True
        return False

    def get_csv_rows(self, parser):
        result = []
        for idx, stop in enumerate(self.stops):
            result.append(self.get_csv_row(idx, parser, stop))
        return result

    def get_csv_row(self, idx, parser, stop):
        result = {'train_num': self.train_num,
                  'start_date': self.get_start_date().isoformat(),
                  'index': idx,
                  'valid': 1 if self.is_valid else 0,
                  'is_first': 1 if idx == 0 else 0,
                  'is_last': 1 if 1 + idx == len(self.stops) else 0,
                  'stop_id': stop.stop_id,
                  'stop_name': stops_utils.get_stop_name(stop.stop_id),
                  'is_real_stop': 1 if stops_utils.is_real(stop.stop_id) else 0,
                  'data_file': os.path.basename(parser.ifile),
                  'data_file_line': stop.line,
        }
        result['data_file_link'] = 'http://localhost:8000/raw-data/?file={0}?line={1}'.format(result['data_file'],
                                                                                              result['data_file_line'])
        result['trip_id'] = '%s_%s' % (result['train_num'],self.get_start_date().strftime('%Y%m%d'))
        attrs = ['actual_arrival', 'exp_arrival', 'actual_departure', 'exp_departure']
        for attr in attrs:
            val = getattr(stop, attr)
            result[attr] = val.isoformat() if val else ''
        da = stop.get_delay_arrival()
        dd = stop.get_delay_departure()
        result['delay_arrival'] = da if da is not None else ''
        result['delay_departure'] = dd if dd is not None else ''

        return result

    def __str__(self):
        return self.__unicode__()

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
                raise CheckException(ERROR_EXP_ARRIVAL_NONE, 'stop index %d' % idx)
        for idx, stop in enumerate(self.stops[0:-1]):
            if stop.exp_departure is None:
                raise CheckException(ERROR_EXP_DEPARTURE_NONE, 'stop index %d' % idx)

                # for idx, stop in enumerate(self.stops):
                #if (stop.actual_arrival is None and stop.exp_arrival is not None
                #    or stop.actual_departure is None and stop.exp_departure is not None):
                #    raise CheckException(ERROR_MISSING_SAMPLE,'stop index %d' % idx)

        for idx in xrange(1, len(self.stops)):
            self.check_gap(idx - 1, idx)

        for idx in xrange(1, len(self.stops)):
            self.check_csv_incr(idx - 1, idx)

        for idx in xrange(len(self.stops)):
            self.check_delay(idx)


    def check_delay(self, idx):
        stop = self.stops[idx]
        delay_arrive = stop.get_delay_arrival()
        if delay_arrive is not None and abs(
                delay_arrive) > DELAY_THRESHOLD:
            raise CheckException(ERROR_ARRIVE_DELAY_TOO_LONG, 'stop index %d' % idx)
        delay_departure = stop.get_delay_departure()
        if delay_departure is not None and abs(
                delay_departure) > DELAY_THRESHOLD:
            raise CheckException(ERROR_DEPARTURE_DELAY_TOO_LONG, 'stop index %d' % idx)

    def check_csv_incr(self, early_idx, late_idx):
        early_stop = self.stops[early_idx]
        late_stop = self.stops[late_idx]
        if early_stop.line >= late_stop.line:
            raise CheckException(ERROR_DECR_CSV, 'stop indexes %d %d' % (early_idx, late_idx))

    def check_gap(self, early_idx, late_idx):
        early_stop = self.stops[early_idx]
        late_stop = self.stops[late_idx]
        attrs = ['actual_arrival', 'exp_arrival', 'actual_departure', 'exp_departure']
        for attr in attrs:
            late_time = getattr(late_stop, attr)
            early_time = getattr(early_stop, attr)
            if not early_time or not late_time:
                return
            gap = (late_time - early_time).total_seconds()
            if gap < 0:
                raise CheckException(ERROR_NEGATIVE_GAP, 'stop indexes %d %d' % (early_idx, late_idx))
            if gap > MAX_GAP:
                raise CheckException(ERROR_GAP_TOO_LONG, 'stop indexes %d %d' % (early_idx, late_idx))


class StopLine(object):
    def parse_time(self, t):
        t = int(t)
        if t == 0:
            return None
        m = t % 100
        h = (t - t % 100) / 100
        return h, m

    def build_datetime(self, hm, offset=0):
        dt = datetime.datetime(year=self.date.year, month=self.date.month, day=self.date.day) + datetime.timedelta(
            hours=hm[0] + 24 * offset, minutes=hm[1])
        return ISRAEL_TZ.localize(dt)

    def find_offset(self, main_hm, hm):
        if main_hm[0] >= 22 and hm[0] <= 3:
            # hm is tomorrow
            return +1
        elif main_hm[0] < 3 and hm[0] >= 22:
            # hm is still yesterday
            return -1
        else:
            return 0

    def build_times(self, gd):
        # now convert each h:m into date
        # these are the rules
        # if there is exp arrival, then this is its date, and all has to be according
        for key in ['exp_arrival', 'actual_arrival', 'actual_departure', 'exp_departure']:
            setattr(self, key, None)
        ea_hm = self.parse_time(gd['exp_arrival'])
        ed_hm = self.parse_time(gd['exp_departure'])
        if ea_hm is not None:
            main_hm = ea_hm
        elif ed_hm:
            main_hm = ed_hm
        else:
            assert False, 'no exp arrival and no exp departure'
        for key in ['exp_arrival', 'actual_arrival', 'actual_departure', 'exp_departure']:
            hm = self.parse_time(gd[key])
            if hm is not None:
                offset = self.find_offset(main_hm, hm)
                setattr(self, key, self.build_datetime(hm, offset=offset))

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


    def __str__(self):
        return self.__unicode__()


    def __unicode__(self):
        return '%5d %4d %-20s A=%5s(%5s) D=%5s(%5s)' % (self.line,
                                                        self.stop_id,
                                                        self.stop_name,
                                                        self.print_time(self.actual_arrival),
                                                        self.print_time(self.exp_arrival),
                                                        self.print_time(self.actual_departure),
                                                        self.print_time(self.exp_departure))


class TrainParser():
    def __init__(self, input, output=None, append=True):
        self.ifile = input
        self.stop_lines = []
        self.trips = []
        self.get_basename()  # just to check for no errors

    def get_basename(self):
        return os.path.splitext(os.path.basename(self.ifile))[0]

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

    def make_dir(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def print_trips_status(self):
        invalid_trips = [trip for trip in self.trips if not trip.is_valid]
        midnight_trips = [trip for trip in self.trips if trip.is_midnight]
        invalid_midnights = [trip for trip in invalid_trips if trip.is_midnight]
        print 'Total trips: %d' % len(self.trips)
        print 'Midnight trips %d' % (len(midnight_trips))
        print 'Invalid trips: %d' % len(invalid_trips)
        print 'Invalid midnights: %d' % len(invalid_midnights)
        count_by_code = defaultdict(int)
        for invalid_trip in invalid_trips:
            count_by_code[invalid_trip.error.code] += 1
        for code, code_count in count_by_code.iteritems():
            print '    %s: %s' % (code, code_count)
        invalid_file = 'log/invalid_%s.txt' % self.get_basename()
        self.make_dir('log')
        with open(invalid_file, 'w') as invalid_fh:
            for invalid_trip in invalid_trips:
                invalid_fh.write('=' * 80 + '\n')
                invalid_fh.write('TRIP = %s ERROR = %s\n' % (invalid_trip, unicode(invalid_trip.error)))
                invalid_fh.write(invalid_trip.unicode_full() + '\n')
        print 'Invalid details written to %s' % invalid_file


    def split_trips(self, trip_num, stops):
        cur_stops = []
        stops.sort(key=lambda x: x.exp_arrival or x.exp_departure)
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
        import csv

        self.make_dir('output')
        output_csv = 'output/%s.csv' % self.get_basename()
        fieldnames = ['train_num',
                      'start_date',
                      'trip_id',
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
                      'data_file_link'
        ]
        with open(output_csv, 'w') as csv_fh:
            csv_writer = csv.DictWriter(csv_fh, fieldnames=fieldnames)
            csv_writer.writeheader()
            for trip in self.trips:
                rows = trip.get_csv_rows(self)
                for row in rows:
                    csv_writer.writerow(row)
        print 'CSV was writtten to %s' % output_csv

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
            is_real = stops_utils.is_real(stop_id)

            sl = StopLine()
            sl.date = self._parse_date(gd['date'])
            sl.train_num = gd['train_num']
            sl.stop_id = stop_id
            sl.stop_name = stops_utils.get_stop_name(sl.stop_id)
            sl.line = idx + 1  # make it base 1 now, like file editors
            sl.is_real = is_real
            sl.build_times(gd)

            self.stop_lines.append(sl)
        else:
            raise Exception('Illegal line %d at %s' % (idx, self.ifile))

    def check_global_trips(self):
        trip_by_train_num_date = defaultdict(list)
        for trip in self.trips:
            trip_by_train_num_date[(trip.train_num,trip.get_start_date())].append(trip)
        for k,trips in trip_by_train_num_date.iteritems():
            if len(trips) > 1:
                for trip in trips:
                    trip.valid = False
                    trip.error = CheckException(code=ERROR_DUPLICATE_NUM_DATE)

    def main(self):
        self.parse()
        self.build_trips()
        self.check_global_trips()
        self.print_trips_status()
        self.dump()


def main():
    parser = argparse.ArgumentParser('parser')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=False)
    parser.add_argument('--append', required=False, default=True, action='store_true')
    ns = parser.parse_args()
    run(**vars(ns))


def run(input=None, output=None, append=True):
    """
     to debug from ipython, do something like tp = run('sample2.txt')
    """
    tp = TrainParser(input=input, output=output, append=append)
    tp.main()
    return tp


if __name__ == '__main__':
    main()
