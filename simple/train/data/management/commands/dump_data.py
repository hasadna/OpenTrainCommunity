from django.core.management.base import BaseCommand, CommandError
import json
import os
from data.models import Route

class Command(BaseCommand):
    args = ''
    help = 'dump data'

    def add_arguments(self, parser):
        parser.add_argument('--dir',required=True,type=str)

    def handle(self, *args, **options):
        result = []
        dirname = options['dir']
        for route in Route.objects.all():
            result.append({
                'id': route.id,
                'stop_ids': route.stop_ids,
            })
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        fname = os.path.join(dirname,'routes.json')
        with open(fname,'w') as fh:
            json.dump(result, fh,indent=4,sort_keys=True)
        print('Wrote routes to {0}'.format(fname))



