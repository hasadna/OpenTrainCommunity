from django.core.management.base import BaseCommand, CommandError
import json
import os
from data.models import Route, Trip, Sample

class Command(BaseCommand):
    args = ''
    help = 'dump data'

    def add_arguments(self, parser):
        parser.add_argument('--dir',required=True,type=str)

    def handle(self, *args, **options):
        self.dirname = options['dir']
        self.dump_routes()
        self.dump_trips()
        self.dump_services()

    def dump_routes(self):
        routes = []
        for route in Route.objects.all():
            routes.append({
                'id': route.id,
                'stop_ids': route.stop_ids,
            })
        self.dump(routes, 'routes')

    def dump_services(self):
        samples = []
        for sample in Sample.objects.filter(valid=True):
            samples.append({
                'id': sample.id,
                'trip': sample.trip.id,
                #'service': sample.trip.service.id,
                'stop_id': sample.stop_id,
                'index': sample.index,
                'exp_departure': sample.exp_departure.isoformat() if sample.exp_departure else None
            })

        self.dump(samples,'samples')

    def dump_trips(self):
        trips = []
        for trip in Trip.objects.all():
            trips.append({
                'id': trip.id,
                'route_id': trip.route_id,
                'start_data': trip.start_date.isoformat(),
                'x_hour_local': trip.x_hour_local,
                'x_week_day_local': trip.x_week_day_local,
            })
        self.dump(trips, 'trips')


    def dump(self,data,name):
        dirname = self.dirname
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        fname = os.path.join(dirname,'{0}.json'.format(name))
        with open(fname,'w') as fh:
            json.dump(data, fh,indent=4,sort_keys=True)
        print('Wrote routes to {0}'.format(fname))



