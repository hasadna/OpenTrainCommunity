import sys
import os
sys.path.append('../../')
from data.analysis.data_utils import get_samples_by_trip, get_name_by_id
import datetime
import datetime
import numpy as np
from collections import OrderedDict
import networkx as nx

### --------------------------------------------------------------------------------------------------------------------------------------------------------

def check_fifo(time_vec):
  # Validate that a time vector comply to the fifo constrait: t + Dij(t) <= t+1 + Dij(t+1)
   vec1 = time_vec
   vec2 = vec1[1:] + 1
   vec1 = vec1[:-1]

   return sum(vec1 > vec2) == 0

### --------------------------------------------------------------------------------------------------------------------------------------------------------


def fifo_time(time_vec):
  # Takes an input time vec, and transform it to a FIFO constrained time vec

  # time_vec_proc = 5*60 * np.ones_like(time_vec)
  time_vec_proc = np.inf * np.ones_like(time_vec)
  const_vec = time_vec_proc.copy()
  valid_vec = time_vec_proc.copy()
  valid_ind = np.where(time_vec > 0)[0]
  valid_vec[valid_ind] = time_vec[valid_ind]
  grad_vec = np.arange(len(time_vec))
  for ind in range(len(time_vec)):
    tmp_vec = const_vec.copy()
    tmp_vec[ind:] = valid_vec[ind:] + grad_vec[ind:] - ind
    best_ind = np.argmin(tmp_vec)
    time_vec_proc[ind] = tmp_vec[best_ind]

  res_new = check_fifo(time_vec_proc)
  assert res_new, 'Problem with fifo on time_vec!'
  return time_vec_proc

### --------------------------------------------------------------------------------------------------------------------------------------------------------

def create_train_graph(trips):
  # Creates a graph based on the train DB, where each node is a station, and each edge is a train hop between two stations.
  # This graph is time dependent (dynamic)

  # Initialization
  G = nx.DiGraph()
  time_vec_template = np.zeros(24*60, dtype=np.int)
  edge_dict = OrderedDict()
  id2name = {}

  # Create station_id to station_name dictionary

  # Populate the nodes in the graph by stations
  current_station_ids = set([])
  for trip in trips:
    trip_station_ids = set(list(map(lambda x: x.gtfs_stop_id, trips[trip])))
    current_station_ids.update(trip_station_ids)

  for station_id in current_station_ids:
    id2name[station_id] = get_name_by_id(station_id)
    G.add_node(station_id, ind=station_id, label=get_name_by_id(station_id))


  # Gather statistics into a temp edge dictionary
  for trip_id in trips:
    samples = trips[trip_id]
    sample_num = len(samples)
    for sample_idx in range(1, sample_num):
      hop_start = samples[sample_idx-1].exp_departure  # start stations have only depart, end stations have only arrive
      hop_end = samples[sample_idx].exp_arrival
      if (not hop_start is None) and (not hop_end is None):
        hop_time_expected = (hop_end - hop_start).seconds / 60.0 # in minutes
        time_indx = 60 * hop_start.hour + hop_start.minute
        station_id1 = samples[sample_idx-1].gtfs_stop_id
        station_id2 = samples[sample_idx].gtfs_stop_id
        hop_str = str(station_id1) + '_' + str(station_id2)
        if not hop_str in edge_dict:
          edge_dict[hop_str] = time_vec_template.copy()
        edge_dict[hop_str][time_indx] = hop_time_expected

  # Insert edge dictionary into graph structure
  for hop in edge_dict:
    station_id1 = int(hop.partition('_')[0])
    station_id2 = int(hop.partition('_')[2])
    # post process time_vec into FIFO constraint
    time_vec = edge_dict[hop]
    time_vec_proc = fifo_time(time_vec)

    G.add_edge(station_id1, station_id2, w=time_vec_proc)

  return G

### -------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
  max_trips = 10
  date_val1 = datetime.datetime(2015, 5, 15)
  date_val2 = datetime.datetime(2015, 6, 15)

  trips = get_samples_by_trip(date_val1, date_val2, max_trips)
  G = create_train_graph(trips)


  print("Done")
