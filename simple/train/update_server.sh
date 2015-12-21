#!/bin/sh

# script to update the server
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo service apache2 restart



