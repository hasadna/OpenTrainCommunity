#!/usr/bin/env python

import subprocess
import os
import platform
import argparse
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-create', action='store_true')
    parser.add_argument('--restore')
    parser.add_argument('--no-postgres-user', action='store_true')
    parser.add_argument('--dry',action='store_true')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--sudo', action='store_true')
    g.add_argument('--nosudo', action='store_true')
    options = parser.parse_args()

    def run_cmd(cmd):
        if not options.dry:
            subprocess.call(cmd, shell=True)
        else:
            print(cmd)

    use_sudo = platform.system().lower() == 'linux'
    if options.nosudo:
        use_sudo = False
    if options.sudo:
        use_sudo = True
        if use_sudo:
            postgres_cmd = "sudo -u postgres psql"
        else:
            if options.no_postgres_user:
                postgres_cmd = "psql"
            else:
                postgres_cmd = "psql -U postgres"

        run_cmd('python manage.py sqlcreate -D --router=default | ' + postgres_cmd)

    if not (options.no_create or options.restore):
        run_cmd('python manage.py migrate')
    if options.restore:
        if options.no_postgres_user:
            tmp1 = os.path.join(tempfile.gettempdir(),os.path.basename(options.restore))
            with open(options.restore) as fr, open(tmp1,'w') as fh:
                for line in fr:
                    if 'postgres' not in line:
                        fh.write(line)
            options.restore = tmp1

        run_cmd('{0} --set ON_ERROR_STOP=on traindata < {1}'.format(postgres_cmd, options.restore))
        run_cmd('python manage.py clear_cache')
    return 0


if __name__ == '__main__':
    main()
