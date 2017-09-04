"""Functions to help in analysis of website data using ipython notebook"""
import collections
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
  for route_id in range(0, 10000):
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


def get_stats_table():
  """Returns a data table of routes with stats"""
  table = pd.DataFrame()
  for route_id in range(0, 100000):
    print(route_id)
    if os.path.isfile("%scache_%s.json" % (CACHE_PATH, route_id)):
      with open("%scache_%s.json" % (CACHE_PATH, route_id), 'r') as input_file:
        route_data = json.load(input_file)
        for year_month, data in route_data:
          for entry in data:          
            keys = collections.OrderedDict()
            keys["route_id"] = route_id
            keys["year"] = year_month[0]
            keys["month"] = year_month[1]
            keys["week_day"] = entry["info"]["week_day"]
            keys["hours"] = entry["info"]["hours"]
            keys["num_trips"] = entry["info"]["num_trips"]
            url_day = '' if entry['info']['week_day'] == 'all' else entry['info']['week_day']
            url_hours = '' if keys["hours"] == 'all' else '%d-%d' % (keys["hours"][0], keys["hours"][1])            
            keys["url"] = URL_GUI % (int(year_month[0]), int(year_month[1]), int(route_id), url_day, url_hours)            
            if keys["num_trips"] == 0 or keys["num_trips"] < 30:
              continue
            keys = pd.Series(keys)

            stats = pd.Series()
            stops = pd.DataFrame(entry["stops"])            
            get_stat = lambda series, name: series.drop('stop_id').add_prefix(name + '_')
            stats = stats.append(get_stat(stops.mean(), 'mean'))
            stats = stats.append(get_stat(stops.median(), 'median'))
            stats = stats.append(get_stat(stops.std(), 'std'))
            stats = stats.append(get_stat(stops.min(), 'min'))
            stats = stats.append(get_stat(stops.max(), 'max'))
            
            row = pd.Series()
            row = row.append(keys)
            row = row.append(stats)
            if table.columns.size == 0:
              table = pd.DataFrame(index=row.index.tolist())
            table = pd.concat([table, row], axis=1)
  table = table.transpose()
  return table

stats_table = get_stats_table()
print(stats_table.shape)
print("")
json_stats_table = stats_table[['route_id', 'year', 'month', 'week_day', 'hours', 'num_trips', 'url', 'mean_arrival_late_pct']]

json_stats_table.to_json('static/analysis/routes_output_format_records.json', orient='records', lines=True)

# TODO: Add "sudo pip install XlsxWriter" to installation
writer = pd.ExcelWriter('static/analysis/routes_output.xlsx', engine='xlsxwriter')
stats_table.to_excel(writer, sheet_name='Sheet1')
writer.save()
