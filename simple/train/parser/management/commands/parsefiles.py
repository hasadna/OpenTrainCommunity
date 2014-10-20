from django.core.management.base import BaseCommand, CommandError
import parser.parse

class Command(BaseCommand):
    args = ''
    help = 'parse files'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('must give filename')
        for filename in args:
            parser.parse.run(filename)


