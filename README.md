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

Note: Installation of numpy via pip might require fulfilling certain [prerequisites](http://scipy.github.io/devdocs/building/linux.html).

```
sudo apt-get install postgresql libpq-dev
```

# Database setup and import

Best way to start is to download the POSTGRES dump file. 

1. Download the latest sql dump from http://otrain.org/files/dumps/  (you can download the gz file)

```
python restore.py <name-of-sql-file>
```
Note that the script will gunzip the file.
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
Alternativley, you can use fab and run the following commands:
```
fab create_db
fab restore_db:<path-to-sql-gz-file>
```

Now you can start the server.
```
python manage.py runserver 
```


# Troubleshooting
* If you receive the error `fatal error: xlocale.h: No such file or directory`, it is likely due to a glibc [header name change](https://sourceware.org/git/?p=glibc.git;a=commit;h=f0be25b6336db7492e47d2e8e72eb8af53b5506d). One [suggested solution](https://github.com/docker-library/python/issues/112#issuecomment-260723908) is to manually create a symlink to the new name:

  ```
  ln -s /usr/include/locale.h /usr/include/xlocale.h
  ```

 * If you receive the error `symbol __res_maybe_init version GLIBC_PRIVATE not defined in libc.so.6 with link time reference`, it is likely due to a [psycopg bug](https://github.com/psycopg/psycopg2-wheels/issues/2) and can likely be solved by upgrading psycopg2 to a later version like 2.7.3.1.
 
 
 # Files
 
 * Excel files from Israeli railway: http://otrain.org/files/2017/, http://otrain.org/files/2018/
 * Database dump: http://otrain.org/files/dumps/ (look for latest timestamp)
 
