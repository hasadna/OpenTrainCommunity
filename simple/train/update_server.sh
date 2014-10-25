#!/bin/sh
git pull
python manage.py collectstatic --noinput
sudo /etc/init.d/apache2 restart

