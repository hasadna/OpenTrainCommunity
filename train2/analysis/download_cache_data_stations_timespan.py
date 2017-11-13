"""
Downloads route data from the server API. Set DOMAIN to SERVER_DOMAIN for
otrain.org, or to LOCAL_DOMAIN in case you're running a server locally, for faster
processing.
Data is cached in individual files per route in the format shown below, with
the filename route_<route_id>.json

   [
      [[<year>, <month>], [<json response>]],
               ...
      [[<year>, <month>], [<json response>]],
      [[<year>, <month>], [<json response>]]
   ]
"""
import os
import json
import requests
import calendar
import datetime

SERVER_DOMAIN = 'otrain.org'
LOCAL_DOMAIN = '127.0.0.1:8000'
DOMAIN = SERVER_DOMAIN
API_BASE_URL = 'http://{}/api/v1/stats/path-info-full/'.format(DOMAIN)
API_PARAMS = '?from_date={}&to_date={}&origin={}&destination={}'


TIMEZONE_OFFSET = -2*60*60  # NB: this is not perfect due to daylight savings time, only used if USE_MICROSECONDS is True

USE_MICROSECONDS = False  # Use the new format d/m/yyyy instead of microseconds

START_YEAR = 2017;
START_MONTH = 5;
END_YEAR = 2017;
END_MONTH = 7;

def get_connected_stop_id_pairs():
  routes = requests.get('http://{}/api/v1/routes/all'.format(DOMAIN)).json()
  pairs = set()
  for route in routes:
    stop_ids = route['stop_ids']
    for idx1, stop1 in enumerate(stop_ids):
      for stop2 in stop_ids[idx1+1:]:
        pairs.add((stop1, stop2))
  return list(pairs)

if not os.path.exists('cache'):
  print('Creating cache directory...')
  os.makedirs('cache')

stop_id_pairs = get_connected_stop_id_pairs()

count = 0
for origin, destination in stop_id_pairs:
  print('%d/%d: %d_%d' % (count, len(stop_id_pairs), origin, destination))
  count += 1
  if True or not os.path.isfile('cache/cache_%d_%d.json' % (origin, destination)):
    origin_destination_data = []
    for year, months in TIME_PERIODS:
      for month in months:
        days = calendar.monthrange(END_YEAR, END_MONTH)[1]
        from_date = "%d/%d/%d" % (1, START_MONTH, START_YEAR)
        to_date = "%d/%d/%d" % (days, END_MONTH, END_YEAR)
        url = API_BASE_URL + API_PARAMS.format(from_date, to_date, origin, destination)

        try:
          response = requests.get(url=url)
          if response.status_code != 200:
            print('ERROR: Status code not 200 OK on route %d' % route_id)
          else:
            route_info = json.loads(response.text)
            origin_destination_data.append([[year, month], route_info])
        except KeyboardInterrupt:
          print('Exiting')
          exit(1)
        except:
          print('ERROR: Exception receiving response on route %d' % route_id)
    with open('cache/cache_%d_%d.json' % (origin, destination), 'w') as output_file:
      json.dump(origin_destination_data, output_file)
  else:
    print('Route %d skipped--cache file already exists' % route_id)
  
