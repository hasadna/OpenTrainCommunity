#!/bin/sh

# script to update the server
git pull
python manage.py collectstatic --noinput
sudo /etc/init.d/apache2 restart


