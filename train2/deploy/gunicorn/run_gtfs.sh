#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source /home/opentrain/.virtualenvs/opentrain2/bin/activate
cd $DIR
# make sure this is the same port as in nginx conf file
exec gunicorn -p /home/opentrain/gtfs.pid -b 127.0.0.1:9002 -w 2 -t 90 opentrain2.wsgi:application


