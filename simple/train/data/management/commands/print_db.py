from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'print db name sqlite3 or postgres'

    def handle(self, *args, **options):
        if 'sqlite3' in settings.DATABASES['default']['ENGINE']:
            print('sqlite3')
        else:
            print('postgres')



