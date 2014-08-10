import entities
from entities import Station, TrainStop
import manage
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series
import itertools

def display_station_delay_bar_graph(vals_dict, stop_names_list, title, figsize):
  ind = np.arange(len(vals_dict.values()[0]))  # the x locations for the groups
  fig, ax = plt.subplots(figsize=figsize)
  width = 0.35
  colors = ['b','r','y']
  rects = []
  for i, key in enumerate(vals_dict):
    rects.append(ax.barh(ind+i*width, vals_dict[key], width, color=colors[i]))
  
  ax.set_title(title)
  ax.set_xlabel('Percentage')  
  ax.set_yticks(ind+width)
  ax.set_yticklabels( stop_names_list)

  ax2 = ax.twinx()
  ax2.set_yticks(ind+width)
  ax2.set_yticklabels(stop_names_list)
  ax2.invert_yaxis()  
  ax2.set_ylim(ax.get_ylim())  
  
  ax.legend( rects, vals_dict.keys() )
  plt.savefig('../results/on_time_delay_is_{}_minutes.png'.format(minutes), bbox_inches='tight')  
  #plt.show() 

def get_stop_passenger_ratio():
  with open('../data/passenger_stats.txt', 'r') as f:
    lines = f.readlines()
  stop_passenger_ratio = {}
  for line in lines:
    if line.strip():
      split = line.split('\t', 1)
      stop_passenger_ratio[int(split[0])] = float(split[1].strip())
  return stop_passenger_ratio

def get_ontime_percent(trainstops_rush, minutes):
  count = 0  
  for x in trainstops_rush:
    if x.arrive_expected.hour != 0 and x.arrive_actual.hour != 0:
      if x.arrive_actual - x.arrive_expected >= datetime.timedelta(minutes = minutes):
        count += 1
  return int(100 - float(count) / len(trainstops_rush) * 100)

def calc_ontime_data(stops, session, minutes, stop_names):
  data = {}
  for stop_id in stops:
    query = session.query(TrainStop).filter(TrainStop.station_id == stop_id)
    trainstops = query.all()
    trainstops_rush = [x for x in trainstops if (x.arrive_expected.hour > 7 and x.arrive_expected.hour < 10) or (x.arrive_expected.hour > 16 and x.arrive_expected.hour < 19)]
    trainstops_non_rush = list(set(trainstops) - set(trainstops_rush))
    data[stop_id] = {'all': get_ontime_percent(trainstops, minutes), 'non_rush': get_ontime_percent(trainstops_non_rush, minutes), 'rush': get_ontime_percent(trainstops_rush, minutes)}
    #print "{},all={}%,non_rush={}%,rush={}%".format(stop_names[stop_id], data[stop_id]['all'], data[stop_id]['non_rush'], data[stop_id]['rush'])
  return data, trainstops

def calc_passenger_weighted_ontime_percent(stops, stop_passenger_ratio, data):
  passenger_weighted_all = 0
  passenger_weighted_rush = 0
  total_weight = 0
  for stop_id in stops:
    if stop_id in stop_passenger_ratio:
      total_weight += stop_passenger_ratio[stop_id]
      passenger_weighted_all += data[stop_id]['all'] * stop_passenger_ratio[stop_id]
      passenger_weighted_rush += data[stop_id]['rush'] * stop_passenger_ratio[stop_id] 
  return int(passenger_weighted_all/total_weight), int(passenger_weighted_rush/total_weight)

# exclude stops - only from bar graph
def get_ontime_percentage_report_for_given_minutes(minutes, session, exclude_stops=None):
  stop_names = manage.get_stop_names()
  stop_passenger_ratio = get_stop_passenger_ratio()  
  stops = stop_names.keys()

  data, trainstops = calc_ontime_data(stops, session, minutes, stop_names)

  all_vals = [data[x]['all'] for x in stops]  
  rush = [data[x]['rush'] for x in stops]
  non_rush = [data[x]['non_rush'] for x in stops]
  stop_names_list = [stop_names[x] for x in stops]

  exclude_inds = [stops.index(x) for x in exclude_stops]
  order = np.argsort(all_vals)[::-1]
  order = [i for i in order if i not in exclude_inds]
  all_vals_ordered = [all_vals[i] for i in order]
  rush_ordered = [rush[i] for i in order]
  stop_names_list_ordered = [stop_names_list[i] for i in order]

  title = 'Percentage of on-time trains per station. On time is when delay < {} minutes'.format(minutes)
  vals_dict = {"all":all_vals_ordered, "rush":rush_ordered}  
  display_station_delay_bar_graph(vals_dict, stop_names_list_ordered, title, (22.0, 16.0))

  passenger_weighted_all, passenger_weighted_rush = calc_passenger_weighted_ontime_percent(stops, stop_passenger_ratio, data)
  print "Passenger ontime={}%, rush={}% (up to {} minutes delay)".format(passenger_weighted_all, passenger_weighted_rush, minutes)

if __name__ == "__main__":
  session = manage.get_session()
  # excluding stops with less than 1% of passengers:
  exclude_stops = [4170, 8700, 7000, 6300, 4100, 4250, 5410, 4690, 9100, 9000, 700, 4660, 5150, 300, 6700, 5010, 5300, 1300, 8550, 4640, 4800, 2500, 6500, 7500]
  
  for minutes in [1, 4, 5]:
    get_ontime_percentage_report_for_given_minutes(minutes, session, exclude_stops)
  
  
  ## snippet of 2d visualization of lateness on stops vs hours axis:
  #hours = range(0,24)
  #d = {}
  #for hour in hours:
    #d[hour] = Series([0] * len(stops), index=stops)
  #df = DataFrame(d, dtype=float)
  ##df.loc[9900][0] = [0,1,2]
  ##DataFrame(d, index=['d', 'b', 'a'], columns=['two', 'three'])
  #vals = {}
  #for val in itertools.product(*[stops, hours]):
    #vals[val] = []

  #for x in trainstops:
    #arrive_delay = (x.arrive_actual - x.arrive_expected).total_seconds()/60
    #depart_delay = (x.depart_actual - x.depart_expected).total_seconds()/60
    #vals[(x.station_id,x.arrive_expected.hour)].append(arrive_delay)
    #print "{},{},{},{},{},{},{},{},{}".format(x.date, x.train_num, 
                                              #x.arrive_expected,#.strftime('%H:%M'), 
                                              #x.arrive_actual,#.strftime('%H:%M'), 
                                              #arrive_delay, 
                                              #x.depart_expected,#.strftime('%H:%M'), 
                                              #x.depart_actual,#.strftime('%H:%M'), 
                                              #depart_delay, x.station_id)
  #for val in vals:
    #cur_val = vals[val]
    #cur_val = [x if x >= 0 else 0 for x in cur_val]
    #cur_val = [1 if x >= 5 else 0 for x in cur_val]
    #if not cur_val:
      #cur_val = [0]
    #print np.mean(cur_val)
    #df.loc[val[0]][val[1]] = np.mean(cur_val)

  #def format_coord(x, y):
      #col = int(x+0.5)
      #row = int(y+0.5)
      #if col>=0 and col<len(hours) and row>=0 and row<len(stops):
          #print df.loc[stops[row]][col]
          #return '%d %d %f' % (stops[row], col, int(100*df.loc[stops[row]][col]))
      #else:
          #return 'unknown'
  
  #ax = plt.imshow(df.values, interpolation='none')
  #plt.gca().format_coord = format_coord  
  
  
  #plt.gca().set_yticklabels(stops)
  #plt.show()
  #plt.setp(axes, xticks=range(len(stops)), xticklabels=stops)
  
  
  

  #query = session.query(TrainStop).filter(TrainStop.station_id == 4600, TrainStop.arrive_actual - TrainStop.arrive_expected > 5)
  