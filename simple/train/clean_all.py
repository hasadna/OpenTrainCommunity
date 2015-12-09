#!/usr/bin/env python

import subprocess
import os
import platform
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-create',action='store_true')
    parser.add_argument('--restore')
    options = parser.parse_args()

    process = subprocess.Popen(['python', 'manage.py','print_db'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    db = out.decode('utf-8').strip()
    assert db in ['sqlite3','postgres'],'Invalid db: {0}'.format(db)

    print('='*60)
    print('DB is {0}'.format(db))
    print('='*60)

    if db == 'sqlite3':
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
    else:
        if platform.system() == 'Windows':
            postgres_cmd = "psql -U postgres"  # this might also work on Linux but I can't check
        else:
            postgres_cmd = "sudo -u postgres psql"
        subprocess.call('python manage.py sqlcreate -D --router=default | ' + postgres_cmd, shell=True)

    if not (options.no_create or options.restore):
        subprocess.call('python manage.py migrate', shell=True)
    if options.restore:
        subprocess.call('{0} --set ON_ERROR_STOP=on traindata < {1}'.format(postgres_cmd, options.restore), shell=True)


if __name__ == '__main__':
    main()

