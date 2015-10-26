from django.core.management.base import BaseCommand, CommandError
import data.utils
import data.cache_utils
import os

def run_command(cmd):
    res = os.system(cmd)
    assert res == 0,'Failed in command %s' % cmd


class Command(BaseCommand):
    args = ''
    help = 'build services'

    def handle(self, *args, **options):
        data.cache_utils.invalidate_cache()
        data.utils.remove_skip_stops()
        data.cache_utils.invalidate_cache()


