#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source /home/opentrain/.virtualenvs/train2/bin/activate
cd $DIR
python manage.py telegram_bot





