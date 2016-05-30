"""
Downloads route data from the otrain.org server API.
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

API_ALL_ROUTES_URL = 'http://otrain.org/api/v1/routes/all/'

API_BASE_URL = 'http://otrain.org/api/v1/stats/route-info-full/'
API_PARAMS = '?from_date={}&route_id={}&to_date={}' # '?route_id={}&from_date={}&to_date={}'


TIMEZONE_OFFSET = -2*60*60  # NB: this is not perfect due to daylight savings time, only used if USE_MICROSECONDS is True

USE_MICROSECONDS = False  # Use the new format d/m/yyyy instead of microseconds

ROUTES = False
# Uncomment following line to force only certain routes,
# otherwise iterate over all routes.
#ROUTES = [672]

TIME_PERIODS = [[2015, [1, 2, 3, 4, 5, 6]],
                [2014, range(1, 13)],
                [2013, range(1, 13)]]

if not os.path.exists('cache'):
   print('Creating cache directory...')
   os.makedirs('cache')

response = requests.get(API_ALL_ROUTES_URL)
response_json = json.loads(response.text)

if not ROUTES:
   routes_all = []
   for r in response_json:
      routes_all.append(r['id'])
else:
   routes_all = ROUTES

for route_id in routes_all:
   if True or not os.path.isfile('cache/cache_%d.json' % route_id):
      data_for_this_route = []
      for year, months in TIME_PERIODS:
         for month in months:
            days = calendar.monthrange(year, month)[1]
            print('Route %d Year %d Month %d Days %d' % (route_id, year, month, days))
            if USE_MICROSECONDS:
               from_date = datetime.datetime(year, month, 1, 0, 0, 0, 0)
               from_date = (calendar.timegm(from_date.timetuple())+TIMEZONE_OFFSET)
               to_date = datetime.datetime(year, month, days, 0, 0, 0, 0)
               to_date = (calendar.timegm(to_date.timetuple())+TIMEZONE_OFFSET)
               url = API_BASE_URL + API_PARAMS.format(from_date * 1000, route_id, to_date * 1000)
            else:
               from_date = "%d/%d/%d" % (1, month, year)
               to_date = "%d/%d/%d" % (days, month, year)
               url = API_BASE_URL + API_PARAMS.format(from_date, route_id, to_date)

            print(url)
            try:
               response = requests.get(url=url)
               if (200 != response.status_code):
                  print('ERROR: Status code not 200 OK on route %d' % route_id)
               else:
                  route_info = json.loads(response.text)
                  data_for_this_route.append([[year, month], route_info])
            except KeyboardInterrupt:
               print('Exiting')
               exit(1)
            except:
               print('ERROR: Exception receiving response on route %d' % route_id)

      with open('cache/cache_%d.json'%route_id, 'w') as output_file:
         json.dump(data_for_this_route, output_file)
   else:
      print('Route %d skipped--cache file already exists' % route_id)

