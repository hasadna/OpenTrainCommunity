#!/usr/bin/env python 
import glob
import os

CSV_FILES = ['parser/output/01_2013.csv',
             'parser/output/02_2013.csv',
             'parser/output/03_2013.csv',
             'parser/output/04_2013.csv',
             'parser/output/05_2013.csv',
             'parser/output/06_2013.csv',
             'parser/output/07_2013.csv',
             'parser/output/08_2013.csv',
             'parser/output/09_2013.csv',
             'parser/output/10_2013.csv',
             'parser/output/11_2013.csv',
             'parser/output/12_2013.csv',
             'parser/output/2014.csv']

def main():
    for csv in CSV_FILES:
        res = os.system('python manage.py parsecsv %s' % csv)
        assert res == 0,'Failed in command'

if __name__ == '__main__':
    main()



