from io import StringIO
from contextlib import contextmanager

import os
from fabric.api import run, env
from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import sudo, local, put

import datetime

env.user = "opentrain"
#env.hosts = ["otrain.org"]
env.hosts = ["142.93.168.206"]
env.projdir = "/home/opentrain/OpenTrainCommunity/train2"
env.venv_dir = '/home/%s/.virtualenvs/train2' % env.user
env.venv_command = '.  %s/bin/activate' % env.venv_dir
env.wsgi_file = "opentrain/wsgi.py"
env.stats_port = "9000"  # for wsgi
env.app_name = "train2"


@contextmanager
def virtualenv(path):
    with cd(path):
        with prefix(env.venv_command):
            yield


@task
def install_apt():
    packages = [
        'git',
        'postgresql',
        'nginx',
        'uwsgi',
        'uwsgi-plugin-python3',
    ]

    pkgs = " ".join(packages)
    sudo("DEBIAN_FRONTEND=noninteractive apt install -y -q {}".format(pkgs),
         pty=False)


@task
def update_server():
    sudo("apt update")
    sudo("apt --yes upgrade")


@task
def hostname():
    run('hostname')


@task
def pull():
    with cd(env.projdir):
        run("git pull")

@task
def pip():
    with virtualenv(env.projdir):
        run("pip install --upgrade pip")
        run("pip install -r requirements.txt")

@task
def migrate():
    with virtualenv(env.projdir):
        run("python manage.py migrate")
        run("python manage.py collectstatic --noinput")
        run("python manage.py createcachetable")
        run("python manage.py clear_cache")

@task
def build_stops():
    with virtualenv(env.projdir):
        run("python manage.py build_stops")

@task
def restart():
    run("kill -HUP $(cat /home/opentrain/train2.pid)")
    sudo("service nginx reload")
    sudo("service nginx restart")


@task
def deploy():
    pull()
    pip()
    migrate()
    restart()


@task
def backup_db():
    ts = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    out = "/home/opentrain/public_html/files/dumps/db_{}.sql.gz".format(ts)
    sudo("sudo -u postgres pg_dump train2 | gzip > {}".format(out))
    run("ls -lh {}".format(out))


def inline_cmd(cmd):
    lines = [l.strip() for l in cmd.splitlines()]
    return " ".join(lines)


@task
def create_db():
    local("python manage.py sqlcreate -D | sudo -u postgres psql")
    create_guest_cmd = '''
    DROP USER IF EXISTS guest;
    CREATE USER guest  WITH ENCRYPTED PASSWORD 'guest';
    GRANT CONNECT ON DATABASE train2 to guest;
    \c train2
    GRANT USAGE ON SCHEMA public to guest;
    GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO guest;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO guest;
    '''
    local('echo "{}" | sudo -u postgres psql'.format(inline_cmd(create_guest_cmd)))

@task
def restore_db(file):
    assert os.path.exists(file), "cannot find file {}".format(file)
    if file.endswith(".gz"):
        cat_command = "gunzip -c {}".format(file)
    else:
        cat_command = "cat {}".format(file)
    local("{} | python manage.py dbshell".format(cat_command))


@task
def create_csv():
    with virtualenv(env.projdir):
        commands = [
            """COPY data_stop TO '/home/opentrain/public_html/files/dumps-csv/stops.csv' DELIMITER ',' CSV HEADER;""",
            """COPY data_route TO '/home/opentrain/public_html/files/dumps-csv/routes.csv' DELIMITER ',' CSV HEADER;""",
            """COPY data_trip TO '/home/opentrain/public_html/files/dumps-csv/trips.csv' DELIMITER ',' CSV HEADER;""",
            """COPY data_sample TO '/home/opentrain/public_html/files/dumps-csv/samples.csv' DELIMITER ',' CSV HEADER;"""
        ]
        for command in commands:
            run("""echo "{}" | sudo -u postgres psql train2""".format(command))
        with cd("/home/opentrain/public_html/files/dumps-csv/"):
            run("for f in *.csv ; do gzip -f $f; done")



UWSGI_CONF = """
[uwsgi]
plugin = python3
virtualenv = {env.venv_dir}
chdir = {env.projdir}
wsgi-file = {env.wsgi_file}
processes = 4
threads = 1
stats = 127.0.0.1:{env.stats_port}
"""

@task
def create_uwsgi_conf():
    conf = UWSGI_CONF.format(env=env)
    filename = "/etc/uwsgi/apps-available/{app_name}.ini".format(app_name=env.app_name)
    enabled = "/etc/uwsgi/apps-enabled/{app_name}.ini".format(app_name=env.app_name)
    put(StringIO(conf), filename, use_sudo=True)
    sudo("ln -sf {filename} {enabled}".format(filename=filename, enabled=enabled))
    sudo("service uwsgi stop")
    sudo("service uwsgi start")

