#!/usr/bin/env bash
sudo -u postgres pg_dump train2 > /home/opentrain/public_html/files/dumps/db_$(date +'%Y_%m_%d_%H_%M_%S').sql
gzip --keep /home/opentrain/public_html/files/dumps/db_$(date +'%Y_%m_%d_%H_%M_%S').sql

