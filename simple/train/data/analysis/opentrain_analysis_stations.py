"""Functions to help in analysis of website data using ipython notebook"""
import collections
import json
import os
import requests
import pandas as pd

CACHE_PATH = 'cache/'
          
URL_GUI = 'http://otrain.org/#/%d%02d/select-route/%d/%d?day=%s&time=%s'
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

def get_stops_ids():
  """Return a list stop ids from the website API"""
  all_stops = json.loads(requests.get('http://otrain.org/api/v1/stops').text)
  result = []
  for stop_info in all_stops:
    result.append(stop_info['stop_id'])
  return result


def get_stats_table():
  """Returns a data table of routes with stats"""
  table = pd.DataFrame()
  stop_ids = get_stops_ids()
  stop_ids = stop_ids[0:2]
  for origin in stop_ids:
    for destination in stop_ids:
      filename = '%scache_%d_%d.json' % (CACHE_PATH, origin, destination)
      print('%d_%d' % (origin, destination))
      if os.path.isfile(filename):
        with open(filename, 'r') as input_file:
          route_data = json.load(input_file)
          for year_month, data in route_data:
            for entry in data:          
              keys = collections.OrderedDict()
              keys["origin"] = origin
              keys["destination"] = destination              
              keys["year"] = year_month[0]
              keys["month"] = year_month[1]
              keys["week_day"] = entry["info"]["week_day"]
              keys["hours"] = entry["info"]["hours"]
              keys["num_trips"] = entry["info"]["num_trips"]
              url_day = '' if entry['info']['week_day'] == 'all' else entry['info']['week_day']
              url_hours = '' if keys["hours"] == 'all' else '%d-%d' % (keys["hours"][0], keys["hours"][1])            
              keys["url"] = URL_GUI % (int(year_month[0]), int(year_month[1]), origin, destination, url_day, url_hours)            
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
# TODO: Add "sudo pip install XlsxWriter", "pip install xlsxwriter" to installation
writer = pd.ExcelWriter('output_stations.xlsx', engine='xlsxwriter')
stats_table.to_excel(writer, sheet_name='Sheet1')
writer.save()