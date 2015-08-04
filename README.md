Opentrain community data analysis
========================================================================

כחלק מפרויקט רכבת פתוחה, הגשנו בקשה (וקיבלנו!) נתונים על זמני רכבות ל- 2013.
כאן מרוכזים הנתונים הללו יחד עם כלים בסיסיים לקריאה וניתוח שלהם. כל אחד מוזמן להוסיף קוד שמנתח את הנתונים ולהעלות אותו בחזרה לגיט. בקבוצת דיון של הסדנא ניתן להסביר את הניתוחים ולהפנות לקוד. אפשר לחשוב על זה בתור הרחבה של דיון לכזה שכולל כתיבת קוד. הגיט הופך למעין לוח מרכזי שכולם יכולים לראות ולכתוב עליו.

אנו מזמינים אתכם להשתמש בקוד הנ"ל ולספר לקהילה על הדבר הכי משמח ומרגיז שגיליתם בנתונים, או כל דבר אחר שאתם מוצאים.


== Fresh install (on linux)

To clean everything and refresh the data to the following steps

1. Verify that you are not running the project in any shell or runserver
2. source the script clean_all.sh. This will clean your DB and will rebuild it (e.g. it runs python manage.py migrate). Note this needs sudo permissions
```
% pwd
home/eran/work/pkw/OpenTrainCommunity/simple/train

% source clean_all.sh
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

3. Next step is to import the csv files. If you don't have them locally, you copy them from the server.
The url is: http://otrain.org/files/csv/

To make things faster (much faster), copy the .gz files of the monthes that you want. There are 12 files for 2013 01_2013.csv.gz to 12_2013.csv.gz, and one for 2014 - 2014.csv.gz.

If you develop locally, it is usually better just to download 1 or 2 months of 2013...

```
% mkdir /tmp/csv_data
% cd /tmp/csv_data
wget http://otrain.org/files/csv/01_2013.csv.gz
wget http://otrain.org/files/csv/02_2013.csv.gz
wget http://otrain.org/files/csv/03_2013.csv.gz
wget http://otrain.org/files/csv/04_2013.csv.gz
wget http://otrain.org/files/csv/05_2013.csv.gz
wget http://otrain.org/files/csv/06_2013.csv.gz
wget http://otrain.org/files/csv/07_2013.csv.gz
wget http://otrain.org/files/csv/08_2013.csv.gz
wget http://otrain.org/files/csv/09_2013.csv.gz
wget http://otrain.org/files/csv/10_2013.csv.gz
wget http://otrain.org/files/csv/11_2013.csv.gz
wget http://otrain.org/files/csv/12_2013.csv.gz
wget http://otrain.org/files/csv/2014.csv.gz
