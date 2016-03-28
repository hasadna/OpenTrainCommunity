#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source /home/opentrain/.virtualenvs/opentrain/bin/activate
cd $DIR
# make sure this is the same port as in nginx conf file
exec gunicorn -p /home/opentrain/opentrain.pid -b 127.0.0.1:9001 -w 3 -t 90 train.wsgi:application

