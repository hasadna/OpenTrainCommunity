python manage.py sqlcreate -D --router=default | sudo -u postgres psql
python manage.py syncdb --noinput
