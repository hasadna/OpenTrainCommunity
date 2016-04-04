#!/usr/bin/env bash
set -xv
out=/home/opentrain/public_html/files/dumps/db_$(date +'%Y_%m_%d_%H_%M_%S').sql
sudo -u postgres pg_dump train2 > ${out}
gzip --keep ${out}

