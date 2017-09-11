#!/bin/bash

DEPLOY=/home/opentrain/work/OpenTrainCommunity/train2/deploy/
WORK=/home/opentrain/work

#cp $DEPLOY/gunicorn/run_train2.sh $WORK/OpenTrainCommunity/train2/
cp $DEPLOY/gunicorn/run_opentrain.sh $WORK/OpenTrainCommunity/simple/train/
#cp $DEPLOY/gunicorn/run_gtfs.sh $WORK/OpenTrain2/server/

sudo cp $DEPLOY/nginx/opentrain.conf /etc/nginx/sites-available/opentrain.conf

sudo cp $DEPLOY/supervisor/opentrain.conf /etc/supervisor/conf.d/opentrain.conf

sudo service supervisor restart
sudo service nginx reload
sudo service nginx restart

