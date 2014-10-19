from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'import csv'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('must give filename')
        import data.utils
        print 'Importing csv %s' % ' '.join(args)
        data.utils.import_csvs(args)


