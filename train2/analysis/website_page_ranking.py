import os
import sys
import requests
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
#os.environ['DJANGO_SETTINGS_MODULE']='train.settings'

#import data.api
import json
#from data.models import Route

# all data for specific routes separately, generated from save_data function
DATA_FILE = os.path.expanduser('~/tmp/res.txt')
base_url = 'http://otrain.org/api/v1/stats/route-info-full?route_id={}'
start_end_dates_url = 'http://otrain.org/api/v1/general/dates-range/'

def save_data():
  """Saves data from route-info-full endpoint to file"""
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
  """Prints list of least and most delayed routes"""
  with open(DATA_FILE, 'r') as outfile:
    all_data = json.load(outfile)

  route_ids = all_data[0]
  route_info_list = all_data[1]
  scores = []
  urls = []
  num_trips = []
  start_end_dates = json.loads(requests.get(url=start_end_dates_url).text)
  start_date = str(start_end_dates['first_date']['year']) + str(start_end_dates['first_date']['month'])
  end_date = str(start_end_dates['last_date']['year']) + str(start_end_dates['last_date']['month'])
  date_range = start_date + '-' + end_date
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
        url = 'http://otrain.org/#/{}/routes/{}'.format(date_range, route)
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
  """
  Graph demonstrating change in lateness at each
  stop as the route progresses from source to destination
  Data used is provided by save_data function
  """

  # For saving to file without X display
  # import matplotlib
  # matplotlib.use('Agg')
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
  # For saving to file without X display; must also disable plt.show
  # plt.savefig('route_lateness_vs_progression.png')

res = analyse2()
#save_data()
#analyse()
