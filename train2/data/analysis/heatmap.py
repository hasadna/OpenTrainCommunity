from bokeh.io import output_file, show
from bokeh.models import (GMapPlot, GMapOptions, ColumnDataSource, Circle, \
                          DataRange1d, PanTool, WheelZoomTool, BoxSelectTool)


import sys
sys.path.append('../../')
from data.analysis.data_utils import get_samples_by_trip, get_name_by_id, get_loc_by_id
import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict
import numpy as np
from  data.analysis.create_train_graph_module import create_train_graph
from data.analysis.graph_module import dynamic_all_to_one


def evaluate_station_coverage(date_val1, date_val2, target_station_id,  day_part='monrning', max_trips=10**6):
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
    morning_indx = [7*60, 12*60]
    noon_indx = [12*60, 17*60]
    evening_indx = [17*60, 22*60]
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

def create_heatmap(station_scores, plot_width=1000, plot_height=600):
    map_options = GMapOptions(lat=32.06, lng=34.87, map_type="roadmap", zoom=9)
    cmap = plt.get_cmap('jet')
    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="Israel"
    )
    plot.plot_width = plot_width
    plot.plot_height = plot_height
    lat_vec = list(map(lambda x: get_loc_by_id(x).lat, station_scores.keys()))
    lon_vec = list(map(lambda x: get_loc_by_id(x).lon, station_scores.keys()))

    for ind, station in enumerate(station_scores):

        source = ColumnDataSource(
            data=dict(
                lat=[lat_vec[ind]],
                lon=[lon_vec[ind]],
            )
        )
        cmap_indx = int(station_scores[station]*cmap.N)
        cmap_val = tuple(np.floor(255 * np.array(cmap(cmap_indx)[:3])))
        circle = Circle(x="lon", y="lat", size=17, fill_color=cmap_val, fill_alpha=0.95, line_color=None)
        plot.add_glyph(source, circle)

    plot.add_tools(PanTool(), WheelZoomTool())
    output_file("Mean Time to Tel-Aviv Hashalom.html")
    show(plot)

### ---------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    date_val1 = datetime.date(2015, 5, 18)
    date_val2 = datetime.date(2015, 5, 18)
    target_station = 4600


    station_scores = evaluate_station_coverage(date_val1, date_val2, target_station,  day_part='monrning', max_trips=10**6)

    create_heatmap(station_scores)