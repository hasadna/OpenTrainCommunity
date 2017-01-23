from contextlib import contextmanager

from fabric.api import run, env
from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import sudo

env.user = "opentrain"
env.hosts = ["otrain.org"]
env.key_filename = "/home/eran/.ssh/id_rsa.pub"
env.projdir = "/home/opentrain/work/OpenTrainCommunity/train2"
env.venv_dir = '/home/%s/.virtualenvs/train2' % env.user
env.venv_command = '.  %s/bin/activate' % env.venv_dir

@contextmanager
def virtualenv(path):
    with cd(path):
        with prefix(env.venv_command):
            yield

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
def restart():
    run("kill -HUP $(cat /home/opentrain/train2.pid)")
    sudo("service nginx reload")
    sudo("service nginx restart")



@task
def update_server():
    pull()
    pip()
    migrate()
    restart()


