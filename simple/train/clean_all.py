#!/usr/bin/env python

import subprocess
import os
import platform

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

subprocess.call('python manage.py migrate', shell=True)
