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
#http://otrain.org/api/v1/stats/path-info-full/?destination=5200&from_date=1%2F3%2F2016&origin=5000&to_date=1%2F4%2F2016
API_ALL_ROUTES_URL = 'http://{}/api/v1/routes/all/'.format(DOMAIN)
API_BASE_URL = 'http://{}/api/v1/stats/route-info-full/'.format(DOMAIN)
API_PARAMS = '?from_date={}&route_id={}&to_date={}'


TIMEZONE_OFFSET = -2*60*60  # NB: this is not perfect due to daylight savings time, only used if USE_MICROSECONDS is True

USE_MICROSECONDS = False  # Use the new format d/m/yyyy instead of microseconds

ROUTES = False
# Uncomment following line to force only certain routes,
# otherwise iterate over all routes.
#ROUTES = [672]

START_YEAR = 2017;
START_MONTH = 5;
END_YEAR = 2017;
END_MONTH = 7;

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

    end_month_days = calendar.monthrange(END_YEAR, END_MONTH)[1]
    print('Route %d' % (route_id))
    if USE_MICROSECONDS:
      from_date = datetime.datetime(START_YEAR, START_MONTH, 1, 0, 0, 0, 0)
      from_date = (calendar.timegm(from_date.timetuple())+TIMEZONE_OFFSET)
      to_date = datetime.datetime(END_YEAR, END_MONTH, end_month_days, 0, 0, 0, 0)
      to_date = (calendar.timegm(to_date.timetuple())+TIMEZONE_OFFSET)
      url = API_BASE_URL + API_PARAMS.format(from_date * 1000, route_id, to_date * 1000)
    else:
      from_date = "%d/%d/%d" % (1, START_MONTH, START_YEAR)
      to_date = "%d/%d/%d" % (end_month_days, END_MONTH, END_YEAR)
      url = API_BASE_URL + API_PARAMS.format(from_date, route_id, to_date)

    print(url)
    try:
      response = requests.get(url=url)
      if response.status_code != 200:
        print('ERROR: Status code not 200 OK on route %d' % route_id)
      else:
        route_info = json.loads(response.text)
        data_for_this_route.append([[START_YEAR, START_MONTH, END_YEAR, END_MONTH], route_info])
    except KeyboardInterrupt:
      print('Exiting')
      exit(1)
    except:
      print('ERROR: Exception receiving response on route %d' % route_id)
    with open('cache/cache_timespan_%d.json'%route_id, 'w') as output_file:
      json.dump(data_for_this_route, output_file)
  else:
    print('Route %d skipped--cache file already exists' % route_id)

