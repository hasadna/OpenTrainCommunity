from django.core.management.base import BaseCommand, CommandError
import json
from data.models import Route

class Command(BaseCommand):
    args = ''
    help = 'dump routes'

    def add_arguments(self, parser):
        parser.add_argument('--out',mandatory=True,type=str)

    def handle(self, *args, **options):
        result = []
        for route in Route.objects.all():
            result.append({
                'id': route.id,
                'stop_ids': route.stop_ids,
            })
        with open(options['out'],'w') as fh:
            json.dump(result, fh,indent=4,sort_keys=True)
        print('Wrote routes to {0}'.format(options['out']))

        

