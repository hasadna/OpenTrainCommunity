import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
os.environ['DJANGO_SETTINGS_MODULE']='train.settings'

import data.api
import json
from data.models import Route

DATA_FILE = '/home/opentrain/res.txt'

def save_data():
  filters = data.api.Filters(from_date=None,to_date=None)
  routes = Route.objects.all()
  # Remove this:
  #routes = routes[0:1]
  route_ids = []
  route_info_list = []
  for route in routes:
    stops = route.stop_ids
    print route.id
    try:
      route_info = data.api._get_route_info_full(route.id, filters) #  Get all data from server 
      route_info_list.append(route_info)
      route_ids.append(route.id)
    except:
        print 'cannot run', route.id
  
  all_data = [route_ids, route_info_list]
  
  with open(DATA_FILE, 'w') as outfile:
    json.dump(all_data, outfile)
  
def analyse():
  with open(DATA_FILE, 'r') as outfile:
    all_data = json.load(outfile)

  route_ids = all_data[0]
  route_info_list = all_data[1]
  scores = []
  urls = []
  num_trips = []

  for route, route_info in zip(route_ids, route_info_list):
    print route
    for sub_route_info in route_info:
      if (sub_route_info['info']['num_trips'] == 0):
        continue
      stop_values = [float(stop['arrival_late_pct']) for stop in sub_route_info['stops']]

      # stats:
      if len(stop_values)>0 and sub_route_info['info']['num_trips'] > 100:
        stops_avg = float(sum(stop_values))/len(stop_values)
        scores.append(stops_avg)
        num_trips.append(sub_route_info['info']['num_trips'])
        info = sub_route_info['info']
        # otrain.org/ui/routes/#/route-details/13?time=9-12&day=3
        url = 'http://otrain.org/ui/routes/#/route-details/{}?'.format(route)
        if info['week_day'] != 'all':
          url = url + 'day={}'.format(info['week_day'])
        if info['hours'] != 'all':
          url = url + '&time={}-{}'.format(info['hours'][0], info['hours'][1])
        urls.append(url)

  reverse = True
  urls=[url for (score,url) in sorted(zip(scores,urls), reverse=reverse)]
  scores=sorted(scores, reverse=True)

  for i in xrange(100):
    print urls[i]
    print 'arrival late score', scores[i]
    print 'num trips', num_trips[i]
    print ''
  print len(urls)


analyse()
