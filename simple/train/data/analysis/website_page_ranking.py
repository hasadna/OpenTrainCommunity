import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
os.environ['DJANGO_SETTINGS_MODULE']='train.settings'

import data.api
import json
from data.models import Route

filters = data.api.Filters(from_date=None,to_date=None)
routes = Route.objects.all()
routes = routes[0:1]
res_list = []
for route in routes[0:1]:
  stops = route.stop_ids
  res = data.api._get_route_info_full(route.id, filters) # Get all data from server 
  res_list.append(res)

all_route_ids=[route.id for route in routes]
all_results = [all_route_ids, res_list]

with open('/home/opentrain/res.txt', 'w') as outfile:
  json.dump(all_results, outfile)
  

  
with open('/home/opentrain/res.txt', 'r') as outfile:
  all_results = json.load(outfile)

routes = all_results[0]
res_list = all_results[1]
scores = []
urls = []

for route, res in zip(routes, res_list):
  for sub_res in res:
    if (sub_res['info']['num_trips'] == 0):
      continue
    alist = [float(stop['arrival_late_pct']) for stop in sub_res['stops']]

    # stats:
    if len(alist)>0 :
      stops_avg=float(sum(alist))/len(alist)
      scores.append(stops_avg)
      info=sub_res['info']
      # otrain.org/ui/routes/#/route-details/13?time=9-12&day=3
      url = 'otrain.org/ui/routes/#/route-details/{}?'.format(route)
      if info['week_day'] != 'all':
        url = url + 'day={}'.format(info['week_day'])
      if info['hours'] != 'all':
        url = url + 'time={}-{}'.format(info['hours'][0], info['hours'][1])
      urls.append(url)

urls=[url for (score,url) in sorted(zip(scores,urls))]
scores=sorted(scores)

for i in xrange(10):
  print urls[i]
  print scores[i]
