#!/usr/bin/env python

import subprocess
import os
process = subprocess.Popen(['python', 'manage.py','print_db'], stdout=subprocess.PIPE)
out, err = process.communicate()
db = out.decode('utf-8').strip()
assert db in ['sqlite3','postgres'],'Invalid db: {0}'.format(db)

if db == 'sqlite3':
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
else:
    subprocess.call('python manage.py sqlcreate -D --router=default | sudo -u postgres psql',shell=True)

subprocess.call('python manage.py migrate',shell=True)




