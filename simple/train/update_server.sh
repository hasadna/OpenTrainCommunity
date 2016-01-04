#!/bin/sh

# script to update the server
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py clear_cache
sudo service apache2 restart



