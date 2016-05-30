#!/usr/bin/env python

import subprocess
import os
import platform
import argparse
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument("--dry", action="store_true")
    options = parser.parse_args()

    def run_cmd(cmd):
        if not options.dry:
            subprocess.call(cmd, shell=True)
        else:
            print(cmd)

    filename = options.file

    use_sudo = platform.system().lower() == 'Linux'
    postgres_cmd = "sudo -u neuberg psql"
    if options.file.endswith(".gz"):
        run_cmd("gunzip --keep {}".format(options.file))
        filename = options.file[:-3]

    run_cmd('python manage.py sqlcreate -D --router=default | ' + postgres_cmd)
    run_cmd('{} --set ON_ERROR_STOP=on train2 < {}'.format(postgres_cmd,
                                                           filename))
    return 0


if __name__ == '__main__':
    main()
