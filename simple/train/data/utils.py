from data.models import Sample
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
              trip_id,
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




