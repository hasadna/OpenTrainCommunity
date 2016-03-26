# Online Project Documentation

Interactive documentation is available at http://opentraincommunity.readthedocs.org/en/latest/

# Developer Environment Setup

The project runs on Python 3, and we recommend using a virtual environment for development. You can use the following command to setup a virtualenv called `opentrain`:
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
cd OpenTrainCommunity/simple/train
pip install -r requirements.txt
```

**NOTE:** If you are working with postgres, make sure that you install the postgres server, example command shown below
```
sudo apt-get install postgresql libpq-dev
```

**NOTE:** If you plan to work with sqlite3, do the following changes:

1. Edit locally the requirements.txt and remove the line with psycopg2
2. Copy the local_settings.py.sqlite3 into local_settings.py 

# Database setup and import
## Option 1: postgres restore

If you are working with postgres, you can just download the dump file from the server and install it.

**NOTE:** this is much faster and simpler than building from the CSB files (next section), so if you are working with postgres, use this method. It will also enable you to rebuild the DB easily if we change the DB on the server (all the process should take less than 5 minutes)

**NOTE:** If this does not work for you, you can skip to next section and rebuild everything from the raw data.

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

On linux platform you might also have to change l29 in clean_all.py to 
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

## Option 2: build all data from (almost) scratch

To clean everything and refresh the data to the following steps

* Verify that you are not running the project in any shell or runserver
* Run the script python clean_all.py. This will clean your DB and will rebuild it (e.g. it runs python manage.py migrate). Note this needs **sudo** permissions

**IMPORTANT** Make sure that there are no error in the SQL commands. They don't abort the script, so look at the output
```
% cd /home/eran/work/pkw/OpenTrainCommunity/simple/train
% python clean_all.py
```
the clean_all.sh, will clean and rebuild the DB and then run migrate. output is like this:
```
[sudo] password for eran: 
DROP DATABASE
DROP ROLE
CREATE ROLE
CREATE DATABASE
GRANT
Operations to perform:
  Synchronize unmigrated apps: corsheaders, staticfiles, csvparser, messages, browse, train, django_extensions
  Apply all migrations: admin, contenttypes, data, auth, sessions
Synchronizing apps without migrations:
  Creating tables...
    Creating table corsheaders_corsmodel
    Running deferred SQL...
  Installing custom SQL...
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying data.0001_initial... OK
  Applying sessions.0001_initial... OK
```

* Next step is to import the csv files. If you don't have them locally, you copy them from the server.
The url is: http://otrain.org/files/csv/ or http://otrain.org.files/xl

To make things faster (much faster), copy the .gz files of the monthes that you want. There are 12 files for 2013 01_2013.csv.gz to 12_2013.csv.gz, and one for 2014 - 2014.csv.gz.
*The new csv files are generated from excel files, copy them from the xl directory*!!!

If you develop locally, it is usually better just to download 1 or 2 months.

After you donwload gunzip 

```
% mkdir tmp/csv_data # or any other location...
% cd tmp/csv_data
% wget http://otrain.org/files/csv/01_2013.csv.gz
% wget http://otrain.org/files/csv/02_2013.csv.gz
% wget http://otrain.org/files/csv/03_2013.csv.gz
% wget http://otrain.org/files/csv/04_2013.csv.gz
% wget http://otrain.org/files/csv/05_2013.csv.gz
% wget http://otrain.org/files/csv/06_2013.csv.gz
% wget http://otrain.org/files/csv/07_2013.csv.gz
% wget http://otrain.org/files/csv/08_2013.csv.gz
% wget http://otrain.org/files/csv/09_2013.csv.gz
% wget http://otrain.org/files/csv/10_2013.csv.gz
% wget http://otrain.org/files/csv/11_2013.csv.gz
% wget http://otrain.org/files/csv/12_2013.csv.gz
% wget http://otrain.org/files/csv/2014.csv.gz
# now gunzip
% gunzip *.gz
```

* last step is to import all the files. If you choose to import everything, this might take long time (1-2 hours). If you chose to import 1-2 2013 files, this iwll take several minutes
**Note** cd back from the tmp folder
```
% cd /home/eran/work/pkw/OpenTrainCommunity/simple/train
% python manage.py importall tmp/csv_data/*.csv
# GO DRINK COFFEE OR HAVE (LONG) LUNCH...
```
### In case of failures/errors

If you have any errors, during the process, you can rerun it again.
In this case, since you already copied the csv files, you just need to run:
```
python clean_all.py
python manage.py importall.py tmp/csv_data/*.csv
```

# Test setup
To test the setup, run the server locally:
```
python manage.py runserver 
```
Then go to this URL: `http://localhost:8000`

