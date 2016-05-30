import logging
import os

logger = logging.getLogger(__name__)

import sys
sys.path.append('../../')
from data.analysis.data_utils import get_samples_by_trip
import datetime
from collections import OrderedDict
import numpy as np
from  data.analysis.create_train_graph_module import create_train_graph
from data.analysis.graph_module import dynamic_all_to_one


def evaluate_station_coverage(date_val1, date_val2, target_station,  day_part='monrning', max_trips=10**6):
    # Scores each station by its averge wait+commute to the given target function
    # INPUT:
    # dateval1 - start date of trips
    # dateval2 - end date of trips
    # target_station_id - relative to this station all the shortest paths will be calculated
    # day_part- slice the statistics as 'all', 'morning', 'noon' or 'evening'
    # max_trips - limits the number of trips analyzed

    trips = get_samples_by_trip(date_val1, date_val2, max_trips)

    print("Got %d trip.." % (len(trips)))
    G = create_train_graph(trips)

    time_len = 60 * 24
    hour_vec = np.array(range(24 * 60)) / 60
    minuete_vec = np.array(range(24 * 60)) % 60
    time_indx_real = map(lambda x: '%04d' % x, hour_vec * 100 + minuete_vec)

    wait_vec, path_vec = dynamic_all_to_one(G, target_station, time_len)

    station_scores = OrderedDict()
    morning_indx = [7 * 60, 12 * 60]
    noon_indx = [12 * 60, 17 * 60]
    evening_indx = [17 * 60, 22 * 60]
    max_wait_val = 120.0

    for station in wait_vec:
        wait_vals = wait_vec[station]
        if day_part == 'all':
            wait_vals = filter(lambda x: not np.isinf(x), wait_vals)
        elif day_part == 'morning':
            wait_vals = filter(lambda x: not np.isinf(x), wait_vals[morning_indx[0]:morning_indx[1]])
        elif day_part == 'noon':
            wait_vals = filter(lambda x: not np.isinf(x), wait_vals[noon_indx[0]:noon_indx[1]])
        elif day_part == 'evening':
            wait_vals = filter(lambda x: not np.isinf(x), wait_vals[evening_indx[0]:evening_indx[1]])
        wait_vals = np.array(list(wait_vals))
        if len(wait_vals) == 0:
            station_scores[station] = 0
        else:
            station_scores[station] = np.maximum(1 - np.median(wait_vals)/max_wait_val, 0)

    return station_scores


### ---------------------------------------------------------------------------------------------------------------------------------------------


def run(date_val1 = datetime.date(2016, 3, 8), date_val2=datetime.date(2016, 3, 8), target_station_id = 4600, day_part='all'):

    from django.conf import settings
    import os

    station_scores = evaluate_station_coverage(date_val1, date_val2, target_station_id,  day_part='all', max_trips=10**6)

    return station_scores

