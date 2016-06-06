"""Functions to help in analysis of website data using ipython notebook"""
import json
import os
import requests
import pandas as pd

CACHE_PATH = 'cache/'
URL_GUI = 'http://otrain.org/#/%d%02d/routes/%d?day=%s&time=%s'
WEEK_DAYS = [1, 2, 3, 4, 5, 6, 7]
HOURS = ['all',
         [4, 7],
         [7, 9],
         [9, 12],
         [12, 15],
         [15, 18],
         [18, 21],
         [21, 24],
         [24, 28],
         ]

def get_stops():
  """Return a list stops from the website API"""
  all_stops = json.loads(requests.get('http://otrain.org/api/v1/stops').text)
  result = {}
  for stop_info in all_stops:
    result.update({stop_info['stop_id']: [stop_info['heb_stop_names'][0], stop_info['stop_name']]})
  return result


def get_routes_above_threshold(num_trips_threshold):
  """Return a list of route ids with trip count above @num_trips_threshold"""
  result = []
  for route_id in xrange(0, 10000):
    passed_filter = False
    if os.path.isfile("%scache_%s.json" % (CACHE_PATH, route_id)):
      with open("%scache_%s.json" % (CACHE_PATH, route_id), 'r') as input_file:
        route_data = json.load(input_file)
        for _, data in route_data:
          for entry in data:
            # Look at either days='all' or hours='all' and limit to minimal num_trip count
            if ((entry['info']['week_day'] == 'all' or entry['info']['hours'] == 'all') and
                entry['info']['num_trips'] > num_trips_threshold):
              passed_filter = True
    if passed_filter:
      result.append(route_id)
  return result


def get_route_by_id(route_id, num_trips_threshold):
  """Return route information by @route_id, filtered by @num_trips_threshold"""
  result = pd.DataFrame()
  with open("%scache_%s.json" % (CACHE_PATH, route_id), 'r') as input_file:
    route_data = json.load(input_file)
    for time, data in route_data:
      for entry in data:
        # Look at either days='all' or hours='all' and limit to minimal num_trip count
        if ((entry['info']['week_day'] == 'all' or entry['info']['hours'] == 'all') and
            entry['info']['num_trips'] > num_trips_threshold):
          url_day = '' if entry['info']['week_day'] == 'all' else entry['info']['week_day']
          url_hours = '' if entry['info']['hours'] == 'all' else '%d-%d' % \
                  (entry['info']['hours'][0], entry['info']['hours'][1])
          if entry['info']['hours'] in HOURS:
            entry['info']['hours'] = HOURS.index(entry['info']['hours'])
          else:
            entry['info']['hours'] = -1
          for stops in entry['stops']:
            stops.update(entry['info'])
            stops.update({'year': time[0], 'month': time[1]})
            stops.update({'url':URL_GUI % (int(time[0]), int(time[1]),
                                           int(route_id), url_day, url_hours)})
            tmp_df = pd.DataFrame(stops, index=[0])
            result = result.append(tmp_df, ignore_index=True)

  return result
