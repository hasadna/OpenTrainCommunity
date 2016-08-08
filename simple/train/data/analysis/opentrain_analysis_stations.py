"""Functions to help in analysis of website data using ipython notebook"""
import collections
import json
import os
import requests
import pandas as pd
import numpy as np

SERVER_DOMAIN = 'otrain.org'
LOCAL_DOMAIN = '127.0.0.1:8000'
DOMAIN = LOCAL_DOMAIN

CACHE_PATH = 'cache/'
          
URL_GUI = 'http://{}/#/%d%02d/select-route/%d/%d?day=%s&time=%s'.format(DOMAIN)
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

import logging

# create logger
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

def get_connected_stop_id_pairs():
  routes = requests.get('http://{}/api/v1/routes/all'.format(DOMAIN)).json()
  pairs = set()
  for route in routes:
    stop_ids = route['stop_ids']
    for idx1, stop1 in enumerate(stop_ids):
      for stop2 in stop_ids[idx1+1:]:
        pairs.add((stop1, stop2))
  return list(pairs)


def get_stops_ids():
  """Return a list stop ids from the website API"""
  all_stops = json.loads(requests.get('http://{}/api/v1/stops'.format(DOMAIN)).text)
  result = []
  for stop_info in all_stops:
    result.append(stop_info['stop_id'])
  return result


def get_stops_ids_to_heb_name():
  """Return a list stop ids from the website API"""
  all_stops = json.loads(requests.get('http://{}/api/v1/stops'.format(DOMAIN)).text)
  result = {}
  for stop_info in all_stops:
    result[stop_info['stop_id']] = stop_info['stop_short_name']
  return result


def get_stats_table():
  """Returns a data table of routes with stats"""
  table = pd.DataFrame()
  stop_id_pairs = get_connected_stop_id_pairs()
  stop_id_to_name = get_stops_ids_to_heb_name()
  #stop_id_pairs = stop_id_pairs[0:50]
  count = 0
  all_rows = []
  columns = []
  for origin, destination in stop_id_pairs:
    filename = '%scache_%d_%d.json' % (CACHE_PATH, origin, destination)
    logmsg = '%d/%d: %d_%d' % (count, len(stop_id_pairs), origin, destination)
    print(logmsg)
    count += 1
    if os.path.isfile(filename):
      with open(filename, 'r') as input_file:
        route_data = json.load(input_file)
        for year_month, data in route_data:
          for entry in data:
            #if entry['info']['week_day'] != 'all' and entry["info"]["hours"] != 'all':
              #continue
            if entry["info"]["num_trips"] == 0 or entry["info"]["num_trips"] < 30:
              continue
            if year_month[0] == 2015:
              continue

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

            stop1 = entry["stops"][0]
            stop2 = entry["stops"][1]
            stats = collections.OrderedDict()
            # Take departure from 1st stop and arrival to 2nd stop.
            stats['arrival_early_pct'] = stop2['arrival_early_pct']
            stats['arrival_late_pct'] = stop2['arrival_late_pct']
            stats['departure_early_pct'] = stop1['departure_early_pct']
            stats['departure_late_pct'] = stop1['departure_late_pct']


            heb_to = " ל"
            everyday_heb = " כל יום "
            aleph = "א"
            bet = "ב"
            gimel = "ג"
            daled = "ד"
            hey = "ה"
            vav = "ו"
            shabbat = "ש"
            days = ["stub", aleph, bet, gimel, daled, hey, vav, shabbat]
            between_hours = "בין השעות "
            delays = " איחורים"
            day_heb = "" if keys["week_day"] == 'all' else days[keys["week_day"]] + " "
            hours_heb = "" if keys["hours"] == 'all' else between_hours + str(keys["hours"][0]) + "-" + str(keys["hours"][1])
            keys["heb_sentence"] = stop_id_to_name[origin] + heb_to + stop_id_to_name[destination] + everyday_heb + day_heb + hours_heb + " " + "{0:.0f}%".format(stats['arrival_late_pct'] * 100) + delays


            row = []
            row += keys.values()
            row += stats.values()
            
            if table.columns.size == 0:
              columns = [x for x,y in keys.items()] + [x for x,y in stats.items()]
            ind = len(table)
            all_rows.append(row)
  table = pd.DataFrame(all_rows, columns=columns)

  return table


def get_all_data():
  """Returns a data table of routes with stats"""
  stop_id_pairs = get_connected_stop_id_pairs()
  count = 0
  all_data = []
  for origin, destination in stop_id_pairs:
    filename = '%scache_%d_%d.json' % (CACHE_PATH, origin, destination)
    logmsg = '%d/%d: %d_%d' % (count, len(stop_id_pairs), origin, destination)
    print(logmsg)
    count += 1
    if os.path.isfile(filename):
      with open(filename, 'r') as input_file:
        route_data = json.load(input_file)
        all_data.append(route_data)
  return all_data


stats_table = get_stats_table()
print(stats_table.shape)
print("")
stats_table.to_csv('output_stations.csv', sep='\t')
# TODO: Add "sudo pip install XlsxWriter", "pip install xlsxwriter" to installation
writer = pd.ExcelWriter('output_stations.xlsx', engine='xlsxwriter')
stats_table.to_excel(writer, sheet_name='Sheet1')
writer.save()