from django.core.management.base import BaseCommand, CommandError
import csvparser.parse


class Command(BaseCommand):
    args = ''
    help = 'parse files'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('must give filename')
        for filename in args:
            csvparser.parse.run(filename)


