# Online Project Documentation

Interactive documentation is available at http://opentraincommunity.readthedocs.org/en/latest/

# Developer Environment Setup

The project runs on Python 3 with POSTGRES, and we recommend using a virtual environment for development. You can use the following command to setup a virtualenv called `opentrain`:
```
mkvirtualenv -p $(which python3) opentrain
```

You might need to first install the virtualenv package, via:
```
sudo pip install virtualenv
```

Then activate the environment:
```
cd opentrain
source bin/activate
```

Then install all of the required modules into your virtualenv using `pip`:
```
cd OpenTrainCommunity/train2
pip install -r requirements.txt
```

```
sudo apt-get install postgresql libpq-dev
```

# Database setup and import

Best way to start is to download the POSTGRES dump file. 

1. Download the latest sql dump from http://otrain.org/files/dumps/ 
2. gunzip it locally 
3. Then run:
```
python clean_all.py --restore <name-of-sql-file>
```
You might need to run,

```
pip install argparse
```

In case you have already set a postgres user name, you could face: 
```
ERROR:  role "postgres" does not exist
```
In this case, create a user name postgres before running the script.

On mac platform you might also have to change l29 in clean_all.py to 
```
postgres_cmd = "sudo -u your_macuser psql"
```

For example, on Linux run the following commands:
```
cd /home/eran/work/pkw/OpenTrainCommunity/simple/train
wget http://otrain.org/files/dumps/db_2015_12_09_02_35_04.sql.gz 
gunzip db_2015_12_09_02_35_04.sql.gz
python clean_all.py --restore db_2015_12_09_02_35_04.sql
rm db_2015_12_09_02_35_04.sql # unless you want to keep it
```

Now you can start the server.
```
python manage.py runserver 
```

