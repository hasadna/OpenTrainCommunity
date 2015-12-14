import src.manage
import datetime
import numpy as np
import matplotlib.pyplot as plt
import src.manage
from graph_modlue import dynamic_all_to_one, display_graph
from creat_train_graph_module import create_train_graph, station_id2name


def analyze_average_commute(date_val):
    # Display a contiguous commute time from a source station to a target station

    # Get DB data
    session = src.manage.get_session()
    stop_names = src.manage.get_stop_names()
    station_id_dict = station_id2name('../data/stops_ids_and_names.txt')
    # Create a graph representation of the train stops
    G = create_train_graph(session, stop_names, station_id_dict, date_val)

    target = 4600   # station_id for Tel-Aviv Hashalom
    time_len = 60*24
    hour_vec = np.array(range(24*60))/60
    minute_vec = np.array(range(24*60)) % 60
    time_indx_real = map(lambda x: '%04d'%x, hour_vec*100 + minute_vec)

    # Calculation of the DOT graph algorithms
    dist_vec, path_vec = dynamic_all_to_one(G, target, time_len)

    display_graph(G, draw_edge_label=False)

    station_id = 5410
    xindx = range(len(time_indx_real))
    plt.xticks(xindx[240::240], time_indx_real[240::240]), plt.plot(xindx[240:], dist_vec[station_id][240:], label=station_id_dict[station_id], linewidth=2.5), plt.grid(),  plt.ylim(0, 150)
    plt.xlabel('time of day'), plt.ylabel('time of commute in minutes'), plt.title(('Commute Time to %s') % (station_id_dict[4600]))
    station_id = 3500
    plt.plot(xindx[240:], dist_vec[station_id][240:], label=station_id_dict[station_id], linewidth=2.5)
    station_id=8700
    plt.plot(xindx[240:], dist_vec[station_id][240:], label=station_id_dict[station_id], linewidth=2.5)
    plt.legend()
    plt.show()




### ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    date_val = datetime.date(2014, 1, 1)
    analyze_average_commute(date_val)