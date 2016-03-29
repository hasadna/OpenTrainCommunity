#!/bin/bash

source /home/opentrain/.virtualenvs/train2/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate

python manage.py collectstatic --noinput

kill -HUP $(cat /home/opentrain/train2.pid)

sudo service nginx reload
sudo service nginx restart







