#!/bin/bash

source /home/opentrain/.virtualenvs/train2/bin/activate
cd "$(dirname "${BASH_SOURCE[0]}")"
python manage.py build_daily_gtfs_data

# PUT THE BELOW IN /etc/cron.d/daily_gtfs

# ###############################
# # CRON TO DOWNLOAD GTFS
# ###############################
# 0 1 * * * opentrain /home/opentrain/OpenTrainCommunity/train2/build_daily_gtfs_data.sh >> /home/opentrain/cron.log 2>&1

