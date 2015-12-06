import src.manage
import datetime
from entities import Station, TrainStop
import numpy as np
from collections import OrderedDict
import networkx as nx


def station_id2name(file_path):
  f = open(file_path, 'r')
  f_data = f.readlines()
  id_vec = map(lambda x: int(x.partition(' ')[0]), f_data)
  name_vec = map(lambda x: x.partition(' ')[2].replace('\n', ''), f_data)
  station_id_dict = OrderedDict(zip(id_vec, name_vec))

  return station_id_dict

### --------------------------------------------------------------------------------------------------------------------------------------------------------

def check_fifo(time_vec):
  # Validate that a time vector comply to the fifo constrait:
  #  t + Dij(t) <= t+1 + Dij(t+1)
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

def create_train_graph(session, stop_names, station_id_dict, date_val=None):

  # Creates a graph based on the train DB, where each node is a station, and each edge is a train hop between two stations.
  # This graph is time dependent (dynamic)

  # Parameters
  sample_limit = 10 ** 9  # How many train stops will be loaded from the DB

  # Query database
  query = session.query(TrainStop).filter(TrainStop.date == date_val)
  trainstops = query.limit(sample_limit).all()

  # Initialization
  G = nx.DiGraph()
  sample_num = len(trainstops)
  for station_id in station_id_dict:
        G.add_node(station_id, ind=station_id, label=station_id_dict[station_id])

  time_vec_template = np.zeros(24*60)
  edge_dict = OrderedDict()

  # Gather statistics into a temp edge dictionary
  for ind in range(1, sample_num):
    # Extract train stop details
    if trainstops[ind-1].train_num == trainstops[ind].train_num:
      date = trainstops[ind].date
      train_num = trainstops[ind].train_num
      start_time = trainstops[ind-1].depart_expected  # start stations have only depart, end stations have only arrive
      end_time = trainstops[ind].arrive_expected
      hop_time_expected = (end_time - start_time).seconds / 60.0 # in minutes
      time_indx = 60 * start_time.hour + start_time.minute
      station_id1 = trainstops[ind-1].station_id
      station_id2 = trainstops[ind].station_id
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


### -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

  session = src.manage.get_session()
  stop_names = src.manage.get_stop_names()
  station_id_dict = station_id2name('../data/stops_ids_and_names.txt')

  date_val = datetime.date(2014, 1, 1)
  G = create_train_graph(session, stop_names, station_id_dict, date_val)

  print "Done"


