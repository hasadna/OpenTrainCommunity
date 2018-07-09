"""Functions to help in analysis of website data using ipython notebook"""
"""
Running the script saves JSON, XLS files with various stats
on a per-route basis. Depends on pre-cached route data sitting in a
cache directory (supplied by the download_cache_data_routes_timespan script)
"""
import collections
import json
import os
import requests
import pandas as pd
import analysis_utils

DOMAIN = 'otrain.org'
CACHE_PATH = 'cache/'
URL_GUI = 'http://otrain.org/#/%d%02d-%d%02d/routes/%d?day=%s&time=%s'
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


def get_stops_ids_to_heb_name(all_stops):
  """Return a map from stop id to Hebrew name"""
  result = {}
  for stop_info in all_stops:
    result[stop_info['stop_id']] = stop_info['stop_short_name']
  return result


def get_stats_table(stop_id_to_name):
  """Returns a data table of routes with stats"""
  table = pd.DataFrame()
  for route_id in range(0, 10000):
    print(route_id)
    if os.path.isfile("%scache_timespan_%s.json" % (CACHE_PATH, route_id)):
      with open("%scache_timespan_%s.json" % (CACHE_PATH, route_id), 'r') as input_file:
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
            keys["url"] = URL_GUI % (int(year_month[0]), int(year_month[1]), int(year_month[2]), int(year_month[3]), int(route_id), url_day, url_hours)            
            if keys["num_trips"] == 0 or keys["num_trips"] < 30:
              continue
            keys["first_stop"] =  entry['stops'][0]['stop_id']
            keys["last_stop"] = entry['stops'][-1]['stop_id']
            keys["first_stop_hebrew"] = stop_id_to_name[entry['stops'][0]['stop_id']]
            keys["last_stop_hebrew"] = stop_id_to_name[entry['stops'][-1]['stop_id']]
            keys["last_stop_arrival_late_pct"] = entry['stops'][-1]['arrival_late_pct']
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

all_stops = json.loads(requests.get('http://{}/api/v1/stops'.format(DOMAIN)).text)
stop_id_to_name = get_stops_ids_to_heb_name(all_stops)

stats_table = get_stats_table(stop_id_to_name)
print(stats_table.shape)
print("")
json_stats_table = stats_table[['route_id', 'year', 'month', 'week_day', 'hours', 'num_trips',
    'url', 'first_stop', 'last_stop', 'last_stop_arrival_late_pct', 'mean_arrival_late_pct',
    'max_arrival_late_pct']]

route_json_path = os.path.join(analysis_utils.STATIC_ANALYSIS_DIR, 'routes_output_format_records.json')
route_xls_path = os.path.join(analysis_utils.STATIC_ANALYSIS_DIR, 'routes_output.xlsx')

json_stats_table.to_json(route_json_path, orient='records', lines=True)

excel_stats_table = stats_table[['year', 'month', 'week_day', 'hours', 'num_trips',
    'url', 'first_stop_hebrew', 'last_stop_hebrew', 'last_stop_arrival_late_pct', 'mean_arrival_late_pct',
    'max_arrival_late_pct']]
percent_columns = ['last_stop_arrival_late_pct', 'mean_arrival_late_pct', 'max_arrival_late_pct']
excel_stats_table.loc[:, percent_columns] *= 100
# TODO: Add "sudo pip install XlsxWriter" to installation
writer = pd.ExcelWriter(route_xls_path, engine='xlsxwriter')
excel_stats_table.to_excel(writer, sheet_name='Sheet1')
writer.save()
