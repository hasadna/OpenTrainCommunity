from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
)
import sys
sys.path.append('../../')
from data.analysis.data_utils import get_samples_by_trip, get_name_by_id, get_loc_by_id
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import OrderedDict
import numpy as np
from  data.analysis.create_train_graph_module import create_train_graph
from data.analysis.graph_module import dynamic_all_to_one


def create_heatmap(station_scores):
    map_options = GMapOptions(lat=32.06, lng=34.87, map_type="roadmap", zoom=11)

    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="Austin"
    )

    lat_vec = list(map(lambda x: get_loc_by_id(x).lat, station_scores.keys()))
    lon_vec = list(map(lambda x: get_loc_by_id(x).lon, station_scores.keys()))

    source = ColumnDataSource(
        data=dict(
            lat=lat_vec,
            lon=lon_vec,
        )
    )

    circle = Circle(x="lon", y="lat", size=15, fill_color=(255, 0, 0), fill_alpha=0.9, line_color=None)
    plot.add_glyph(source, circle)

    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
    output_file("Mean Time to Tel-Aviv Hashalom.html")
    show(plot)

if __name__ == '__main__':
    date_val1 = datetime.date(2015, 5, 15)
    date_val2 = datetime.date(2015, 5, 15)

    max_trips = 100
    trips = get_samples_by_trip(date_val1, date_val2, max_trips)


    print("Got %d trip.." % (len(trips)))
    G = create_train_graph(trips)

    target = 4600
    time_len = 60 * 24
    hour_vec = np.array(range(24 * 60)) / 60
    minuete_vec = np.array(range(24 * 60)) % 60
    time_indx_real = map(lambda x: '%04d' % x, hour_vec * 100 + minuete_vec)

    # dist_vec, path_vec = dynamic_all_to_one(G, target, time_len)

    station_scores = OrderedDict(zip(G.nodes(), np.ones(len(G.nodes()))))

    create_heatmap(station_scores)