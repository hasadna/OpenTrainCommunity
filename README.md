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

If it's already installed, you might need to update it, via:
```
sudo pip install --upgrade virtualenv
```

Then activate the environment:
```
source ~/.virtualenvs/opentrain/bin/activate
```

Then clone the git repository (e.g into ~/devel folder), via:
```
git clone https://github.com/hasadna/OpenTrainCommunity.git
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
Now you can start the server.
```
python manage.py runserver 
```

