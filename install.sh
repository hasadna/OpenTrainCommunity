#!/usr/bin/env bash

sudo apt-get install postgresql postgresql-contrib libpq-dev python-dev
sudo pip install psycopg2
sudo pip install virtualenv virtualenvwrapper
mkvirtualenv opentraincommunity
workon opentraincommunity
pip install -r requirements.txt


user=$USER
sudo su postgres
createdb opentrain_community
psql -c "CREATE USER admin WITH PASSWORD 'admin';"
echo `printf "Changing back to user: %s" user`
su ${user}

python setup_db.py


