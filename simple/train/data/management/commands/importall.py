#!/usr/bin/env python
from django.core.management import BaseCommand
from django.conf import settings
from django.core import cache
from data.utils import invalidate_cache
import os

CSV_DIR = '/home/opentrain/public_html/files/csv'

CSV_FILES = ['01_2013.csv',
             '02_2013.csv',
             '03_2013.csv',
             '04_2013.csv',
             '05_2013.csv',
             '06_2013.csv',
             '07_2013.csv',
             '08_2013.csv',
             '09_2013.csv',
             '10_2013.csv',
             '11_2013.csv',
             '12_2013.csv',
             '2014.csv']


class Command(BaseCommand):
    args = ''
    help = 'Imports all (or specified) CSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument("csv_files",nargs="*")

    def run_command(self, cmd):
        res = os.system(cmd)
        assert res == 0,'Failed in command %s' % cmd

    def handle(self, *args, **options):
        csv_files = options['csv_files']
        is_sqlite3 = settings.USE_SQLITE3
        print('Using sqlite3 = {0}'.format(is_sqlite3))
        invalidate_cache()
        if not csv_files:
            csv_files = []
            for csv in CSV_FILES:
                fullcsv = os.path.join(CSV_DIR,csv)
                csv_files.append(fullcsv)
        print('Will parse the following csv_files:')
        for idx,fullcsv in enumerate(csv_files):
            print('%2d) %s' % (idx,fullcsv))

        for fullcsv in csv_files:
            self.run_command('python manage.py parsecsv %s' % fullcsv)

        print('Building services - takes long time')
        self.run_command('python manage.py build_services')
        invalidate_cache()
        self.run_command('python manage.py remove_skip_stops')
