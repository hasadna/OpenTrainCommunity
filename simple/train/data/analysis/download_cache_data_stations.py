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
DOMAIN = LOCAL_DOMAIN
#http://otrain.org/api/v1/stats/path-info-full/?destination=5200&from_date=1/3/2016&origin=5000&to_date=1/4/2016
API_STOPS_URL = 'http://{}/api/v1/stops/'.format(DOMAIN)
API_BASE_URL = 'http://{}/api/v1/stats/path-info-full/'.format(DOMAIN)
#API_PARAMS = '?from_date={}&route_id={}&to_date={}'
API_PARAMS = '?from_date={}&to_date={}&origin={}&destination={}'


TIMEZONE_OFFSET = -2*60*60  # NB: this is not perfect due to daylight savings time, only used if USE_MICROSECONDS is True

USE_MICROSECONDS = False  # Use the new format d/m/yyyy instead of microseconds

TIME_PERIODS = [[2016, [1, 2, 3]],
                [2015, range(1, 13)]]

if not os.path.exists('cache'):
  print('Creating cache directory...')
  os.makedirs('cache')

response = requests.get(API_STOPS_URL)
response_json = json.loads(response.text)

stop_ids = []
for stop_json in response_json:
  stop_ids.append(stop_json['stop_id'])

stop_ids = stop_ids[0:5]

for origin in stop_ids:
  for destination in stop_ids:
    if True or not os.path.isfile('cache/cache_%d_%d.json' % (origin, destination)):
      origin_destination_data = []
      for year, months in TIME_PERIODS:
        for month in months:
          days = calendar.monthrange(year, month)[1]
          print('Origin %d Destination %d Year %d Month %d Days %d' % (origin, destination, year, month, days))
          from_date = "%d/%d/%d" % (1, month, year)
          to_date = "%d/%d/%d" % (days, month, year)
          url = API_BASE_URL + API_PARAMS.format(from_date, to_date, origin, destination)
  
          print(url)
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
  
