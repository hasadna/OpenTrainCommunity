import os
import sys
import requests
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
#os.environ['DJANGO_SETTINGS_MODULE']='train.settings'

#import data.api
import json
#from data.models import Route

DATA_FILE = os.path.expanduser('~/tmp/res.txt')
base_url = 'http://otrain.org/api/route-info-full?route_id={}'

def save_data():
  route_ids = []
  route_info_list = []
  for route_id in range(1,1000):
    print(route_id)
    try:
      resp = requests.get(url=base_url.format(route_id))
      if resp.status_code == 500:
        break;      
      route_info = json.loads(resp.text)      
      route_info_list.append(route_info)
      route_ids.append(route_id)
    except:
      print('cannot run %s' % route_id)
  
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
    for sub_route_info in route_info:
      if (sub_route_info['info']['num_trips'] == 0):
        continue
      stop_values = [float(stop['arrival_late_pct']) for stop in sub_route_info['stops']]
      stop_values.extend([float(stop['departure_early_pct']) for stop in sub_route_info['stops']])

      # stats:
      if len(stop_values)>0 and sub_route_info['info']['num_trips'] > 500:
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


  print('*** High error to low ***')
  for i in range(25):
    print('arrival late score', scores[i])
    print('num trips', num_trips[i])
    print('')

  print( '*** Low error to high **********************************************************************')
  for i in range(25):
    ind = len(urls) - i - 1
    print( urls[ind])
    print( 'arrival late score', scores[ind])
    print( 'num trips', num_trips[ind])
    print( '')
  print( len(urls))


def analyse2():
  import matplotlib.pyplot as plt
  import numpy as np
  
  with open(DATA_FILE, 'r') as outfile:
    all_data = json.load(outfile)

  route_ids = all_data[0]
  route_info_list = all_data[1]
  x = []
  y = []

  for route, route_info in zip(route_ids, route_info_list):
    print( route)
    for sub_route_info in route_info:
      if (sub_route_info['info']['num_trips'] < 100):
        continue
      stop_values = [float(stop['arrival_late_pct']) for stop in sub_route_info['stops']]
      for idx, val in enumerate(stop_values):
        x.append(idx/float(len(stop_values)))
        y.append(val)

  print( x[0:100])
  print( y[0:100])
  
  k = 12
  means = []
  for i in range(k):
    means.append([])
  
  for xa, ya in zip(x,y):
    if ya:
      means[int(xa*k)].append(ya)
  
  mean_vals = [np.mean(means[i]) for i in range(k)]
  plt.plot([int(float(i)/(k-1)*100) for i in range(k)], mean_vals)
  plt.xlabel('Route percentage')
  plt.ylabel('Percent late')
  plt.title('Route lateness progression')
  plt.show()

res = analyse2()
#save_data()
#analyse()
