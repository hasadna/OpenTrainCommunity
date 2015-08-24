from django.core.management.base import BaseCommand, CommandError
import xlparser.utils

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        files = options['files']
        for f in files:
            xlparser.utils.parse_xl(f)

