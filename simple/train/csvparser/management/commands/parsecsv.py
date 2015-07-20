from django.core.management.base import BaseCommand, CommandError
import data.utils

class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('files', nargs='*')

    def handle(self, *args, **options):
        for filename in options['files']:
            data.utils.import_current_csv(filename)
