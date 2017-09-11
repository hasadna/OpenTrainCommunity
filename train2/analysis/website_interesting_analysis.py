import os
import sys
import requests
import numpy as np
import math

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
# os.environ['DJANGO_SETTINGS_MODULE']='train.settings'

#import data.api
import json
#from data.models import Route

DATA_FILE = os.path.expanduser('~/tmp/res.txt')
base_url = 'http://otrain.org/api/route-info-full?route_id={}'
stops_url = 'http://otrain.org/api/stops'

def save_data():
    route_ids = []
    route_info_list = []
    for route_id in range(1, 1000):
        print(route_id)
        try:
            resp = requests.get(url=base_url.format(route_id))
            if resp.status_code == 500:
                break
            route_info = json.loads(resp.text)
            route_info_list.append(route_info)
            route_ids.append(route_id)
        except:
            print('cannot run %s' % route_id)

    all_data = [route_ids, route_info_list]

    with open(DATA_FILE, 'w') as outfile:
        json.dump(all_data, outfile)

def get_stations_matches():
	resp = requests.get(url=stops_url)


def analyse():
    with open(DATA_FILE, 'r') as outfile:
        all_data = json.load(outfile)

    route_ids = all_data[0]
    route_info_list = all_data[1]
    urls = []

    sub_route_data = []
    for route, route_info in zip(route_ids, route_info_list):
        for i, sub_route_info in enumerate(route_info):
            info = sub_route_info["info"]
            # Taking only general informations for routes that have more than 100 trips
            # to avoid wrong, empty, useless datas
            if info['week_day'] == 'all' and info['hours'] == 'all' and info['num_trips'] > 100:
                url = 'http://otrain.org/api/route-info-full?route_id={}'.format(
                    route)
                urls.append(url)
                late_arrival = {}
                for i, stop in enumerate(sub_route_info["stops"]):
                    if stop.keys():
                	   late_arrival[stop['stop_id']] = stop['arrival_late_pct']
                if late_arrival:
                    sub_route_data.append({
                        "route": route,
                        "url": url,
                        "arrival":
                        {
                            "mean_late": np.mean(late_arrival.values()),
                            "worst_station": max(late_arrival, key=late_arrival.get)
                        }
                    })

    station_ranking = {}
    route_ranking = {}
    for data in sub_route_data:
        worst_station = data['arrival']['worst_station']
        route_ranking[data['url']] = data['arrival']['mean_late']
        if data['arrival']['worst_station'] in station_ranking.keys():
            station_ranking[worst_station] += 1
        else:
            station_ranking[worst_station] = 1



    # Sorting routes by latency mean
    sorted_routes = [(url, late_mean) for url, late_mean in sorted(
        route_ranking.items(), key=lambda x: x[1], reverse=True) if late_mean > 0.0 and late_mean < 1.0]

    # Sorting stations, ranking those that appears to be the most commonly "late"
    num_sub_routes = len(sub_route_data)
    sorted_stations = [(id, "%.2f%%" % ((total/float(num_sub_routes))*100)) for id, total in sorted(
        station_ranking.items(), key=lambda x: x[1], reverse=True)]

    print("Ranking average latency for routes :")
    for i, route in enumerate(sorted_routes):
        print("%s." % (i+1))
        print(route)

    print("Stations with most late trains :")
    for i, station in enumerate(sorted_stations):
        print("%s." % (i+1))
        print(station)

analyse()

