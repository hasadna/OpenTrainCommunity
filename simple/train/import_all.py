#!/usr/bin/env python 
import glob
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

def main(csv_files):
    if not csv_files:
        csv_files = []
        for csv in CSV_FILES:
            fullcsv = os.path.join(CSV_DIR,csv)
            csv_files.append(fullcsv)
    print 'Will parse the following csv_files:'
    for idx,fullcsv in enumerate(csv_files):
        print '%2d) %s' % (idx,fullcsv)
    for fullcsv in csv_files:
        res = os.system('python manage.py parsecsv %s' % fullcsv)
        assert res == 0,'Failed in command'

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_files",nargs="*")
    ns = parser.parse_args()
    main(ns.csv_files)



