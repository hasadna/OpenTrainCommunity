from models import Sample, Trip
import datetime
from django.conf import settings
import pytz

israel_tz = pytz.timezone(settings.TIME_ZONE)

def import_csv(filename,start_line=None,end_line=None):
    lineno = 0
    objects = []
    print 'import_csv filename = %s start_line = %s end_line = %s' % (filename,start_line,end_line)
    inserted = 0
    with open(filename) as fh:
        for lineno,line in enumerate(fh):
            if lineno > 0:
                skip = False
                if start_line and lineno < start_line:
                    skip = True
                if end_line and lineno > end_line:
                    skip = True
                if not skip:
                    objects.append(import_line(line.strip(),lineno))
            if len(objects) == 10000:
                bulk_insert(objects)
                inserted += len(objects)
                print '%s imported' % (inserted)
                objects = []
        bulk_insert(objects)
        inserted += len(objects)
        print '%s imported' % (inserted)
    print 'Total number of samples in DB = %s' % (Sample.objects.count())

def bulk_insert(objects):
    Sample.objects.bulk_create(objects)

def parse_date(dstr):
    y,m,d = [int(x) for x in dstr.split('-')]
    return datetime.date(year=y,month=m,day=d)

def parse_datetime(dtstr):
    #2013-01-27 07:27:00
    dt = datetime.datetime.strptime(dtstr,'%Y-%m-%d %H:%M:%S')
    return israel_tz.localize(dt)

def parse_int(x):
    return int(x)

def parse_float(x):
    return float(x)


def import_line(line,lineno):
    entries = line.split(',')
    assert len(entries) == 10
    s = Sample()
    s.date = parse_date(entries[0])
    s.train_num = parse_int(entries[1])
    s.arrive_expected = parse_datetime(entries[2])
    s.arrive_actual = parse_datetime(entries[3])
    s.arrive_delay = parse_float(entries[4])
    s.depart_expected = parse_datetime(entries[5])
    s.depart_actual = parse_datetime(entries[6])
    s.depart_delay = parse_float(entries[7])
    s.stop_id = parse_int(entries[8])
    s.stop_name = entries[9]
    s.csv_line = lineno
    if s.arrive_actual:
        s.time_in_station = (s.depart_actual - s.arrive_actual).total_seconds()
    else:
        s.time_in_station = 0
    return s

def build_trips():
    all_keys = Sample.objects.values_list('train_num','date').distinct()
    trips = []
    saved_so_far = 0
    for idx,(train_num,date) in enumerate(all_keys):
        trip = Trip()
        trip.date = date
        trip.train_num = train_num
        samples = list(Sample.objects.filter(date=date,train_num=train_num).order_by('arrive_expected'))
        arrive_delays = [s.arrive_delay for s in samples]
        depart_delays = [s.depart_delay for s in samples]
        trip.max_arrive_delay = max(arrive_delays)
        trip.max_depart_delay = max(depart_delays)
        trip.final_delay = arrive_delays[-1]
        trip.stops_count = len(samples)
        trips.append(trip)
        if len(trips) == 1000:
            Trip.objects.bulk_create(trips)
            saved_so_far += len(trips)
            trips = []
            print 'Saved %s trips' % saved_so_far
    Trip.objects.bulk_create(trips)
    print 'Saved %s trips' % saved_so_far



