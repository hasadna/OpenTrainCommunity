#!/usr/bin/env python 
import glob
import os

def main():
    csv_files = list(sorted(glob.glob('parser/output/*_2013.csv')))
    for csv in csv_files:
        res = os.system('python manage.py gensql %s' % csv)
        assert res == 0

if __name__ == '__main__':
    main()



