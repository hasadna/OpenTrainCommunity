from data.models import Sample, Trip
def import_csvs(csv_files):
    results = []
    for csv_file in csv_files:
        before = Sample.objects.all().count()
        error = None
        try:
            import_csv(csv_file)
        except Exception,e:
            error = e
        after = Sample.objects.all().count()
        file_status = {'csv_file': csv_file,
                        'before': before,
                        'after': after,
                         'added' : after - before,
                         'error' : error}
        print file_status
        results.append(file_status)
    print '===================================================================='
    for ls in results:
        print '%-20s %s %s' % (ls['csv_file'],ls['added'],ls['error'])
def import_csv(csv_file):
    import os
    cmd = r"""\copy data_sample(train_num,
              start_date,
              trip_name,
              index,
              stop_id,
              stop_name,
              is_real_stop,
              valid,
              is_first,
              is_last,
              actual_arrival,
              exp_arrival,
              delay_arrival,
              actual_departure,
              exp_departure,
              delay_departure,
              data_file,
              data_file_line,
              data_file_link)
              from '%s' with delimiter ',' CSV HEADER""" % csv_file
    with open('/tmp/import.cmd','w') as fh:
        fh.write(' '.join(cmd.split()))
    os.system('cat /tmp/import.cmd | python manage.py dbshell')


def build_trips():
    """
    note: there is problem with sample with trip name 443_20140330
    since it has no real stops
    """
    from django.db import connection
    before = Trip.objects.count()
    with connection.cursor() as c:
        c.execute("""insert into data_trip(id,train_num,start_date,valid,stop_ids)
        (SELECT trip_name,train_num,start_date,valid,array_agg(stop_id ORDER BY index) AS stop_ids
            FROM public.data_sample
            WHERE is_real_stop and trip_id is null
            GROUP BY trip_name,train_num,start_date,valid)""")
        c.execute('update data_sample set trip_id = trip_name where trip_id is null')
    after = Trip.objects.count()
    print 'Before = %s After = %s Added = %s' % (before,after,after-before)



