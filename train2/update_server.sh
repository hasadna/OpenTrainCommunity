#!/bin/bash

source /home/opentrain/.virtualenvs/train2/bin/activate
git pull
pip install -r requirements.txt

(cd /home/opentrain/work/OpenTrainCommunity/train2/ui/static/ui/RouteExplorer && bower install)

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py clear_cache

kill -HUP $(cat /home/opentrain/train2.pid)

sudo service nginx reload
sudo service nginx restart







