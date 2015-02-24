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

def main():
    for csv in CSV_FILES:
        fullcsv = os.path.join(CSV_DIR,csv)
        res = os.system('python manage.py parsecsv %s' % fullcsv)
        assert res == 0,'Failed in command'

if __name__ == '__main__':
    main()



