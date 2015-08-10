Fresh install (on linux)
========================

To clean everything and refresh the data to the following steps

* Verify that you are not running the project in any shell or runserver
* source the script clean_all.sh. This will clean your DB and will rebuild it (e.g. it runs python manage.py migrate). Note this needs **sudo** permissions

**IMPORTANT** Make sure that there are no error in the SQL commands. They don't abort the script, so look at the output
```
% cd /home/eran/work/pkw/OpenTrainCommunity/simple/train
% source clean_all.sh
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
The url is: http://otrain.org/files/csv/

To make things faster (much faster), copy the .gz files of the monthes that you want. There are 12 files for 2013 01_2013.csv.gz to 12_2013.csv.gz, and one for 2014 - 2014.csv.gz.

If you develop locally, it is usually better just to download 1 or 2 months of 2013...

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
% ./import_all.py tmp/csv_data/*.csv
# GO DRINK COFFEE OR HAVE (LONG) LUNCH...
```
### In case of failures/errors

If you have any errors, during the process, you can rerun it again.
In this case, since you already copied the csv files, you just need to run:
```
% source clean_all.sh
% ./import_all.py tmp/csv_data/*.csv
```
