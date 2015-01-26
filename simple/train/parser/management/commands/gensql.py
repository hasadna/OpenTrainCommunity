from django.core.management.base import BaseCommand, CommandError
import data.utils

class Command(BaseCommand):
    args = ''
    help = 'gen sql'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('must give filename')
        for filename in args:
            data.utils.gen_sql(filename)
