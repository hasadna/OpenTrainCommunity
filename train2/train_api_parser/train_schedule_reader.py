"""Train Schedule Reader that reconstructs the schedule from API calls to Israel Railways"""

import requests
import datetime
import json
import os.path
from time import sleep

STATIONS_API = "http://otrain.org/api/v1/stops"
BASE_URL = "http://moblin.rail.co.il/rail/v01/schedule/?&date={}%2000:00&destination={}&hours=12&origin={}"
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
SLEEP_BETWEEN_REQUESTS_SECONDS = 2

class Station(object):
  """A class that represents a physical station"""
  def __init__(self, station_id, name=None):
    self._station_id = station_id
    self._name = name

  @property
  def station_id(self):
    """Returns the station ID (the old Israel Railways IDs)"""
    return self._station_id

  @property
  def name(self):
    """Returns the English name of the station"""
    return self._name

  def __repr__(self):
    return "{}({})".format(self.station_id, self.name)

  def __str__(self):
    return self.__repr__()


class StopTime(object):
  """A stop of a train at a station in a certain date and time"""
  def __init__(self, station, arrival, departure):
    # Returns the station object associated with this stop
    self.station = station
    # A datetime object, the arrival time of the train to the station
    self.arrival = arrival
    # A datetime object, the departure time of the train from the station
    self.departure = departure

  def __repr__(self):
    return "Stop: {}, Arrival:{} Departure:{}".format(
        self.station.name, self.arrival, self.departure)

class Trip(object):
  """A trip of a train through a series of stations in a certain date and time"""
  def __init__(self, train_number, line_number):
    # Returns a string, the train number, which is unique in a single day
    self.train_number = train_number
    # Returns a string, the line number
    self.line_number = line_number
    # Returns a list of StopTime objects, the stops in this trip, by chronological order
    self.stops = []

  def __repr__(self):
    return "Train: {}, Line:{}".format(self.train_number, self.line_number)

def get_stations():
  """Queries our API and returns a map of stations ID to stations."""
  stations = {}
  response = requests.get(STATIONS_API)
  json_stations = json.loads(response.content)
  for json_station in json_stations:
    station_id = str(json_station["stop_id"])
    stations[station_id] = Station(station_id, json_station["stop_name"])
  return stations

def get_trips_through_tel_aviv(day):
  """Returns all trips that pass one of the stations in Tel Aviv"""
  stations_map = get_stations()
  tel_aviv_stations = [stations_map["3600"], stations_map["3700"],
                       stations_map["4600"], stations_map["4900"]]
  trips_to_tel_aviv = get_trips(day, stations_map.values(), tel_aviv_stations,
                                stations_map)
  trips_from_tel_aviv = get_trips(day, tel_aviv_stations, stations_map.values(),
                                  stations_map)
  return trips_to_tel_aviv + trips_from_tel_aviv

def parse_time(value):
  return datetime.datetime.strptime(value, DATETIME_FORMAT)

def parse_trip(train_json, origin_station, destination_station, stations_map):
  """Parse a Trip object from a json from the Israel Railways API containing trip information"""
  trip = Trip(train_json["Trainno"], train_json["LineNumber"])
  trip.stops.append(StopTime(origin_station, None, parse_time(train_json["DepartureTime"])))
  if not train_json["StopStations"]:
    print "Empty StopStations for trip from {} to {}".format(
        origin_station.name, destination_station.name)
  else:
    stops = train_json["StopStations"]["Station"]
    if type(stops) == dict:
      stops = [stops]
    for stop in stops:
      arrival = parse_time(stop["ArrivalTime"])
      departure = parse_time(stop["DepartureTime"])
      trip.stops.append(StopTime(stations_map[stop["StationId"]], arrival, departure))
  trip.stops.append(StopTime(destination_station, parse_time(train_json["ArrivalTime"]), None))
  return trip

def get_trips(day, origin_stations, destination_stations, stations_map):
  """
   Fetch trips from the Israel Railways API

   Args:
     day: The day to fetch the data for
     origin_stations: A list of Stations, the origin stations to query
     destination_stations: A list of Stations, the destination stations to query
     stations_map: A map from station ID to its Station object
   Return:
     List of Trip objects
  """
  trips = []
  for origin in origin_stations:
    for destination in destination_stations:
      if origin.station_id != destination.station_id:
        url = BASE_URL.format(day.strftime("%d/%m/%y"), destination.station_id, origin.station_id)
        filename = "{}_{}_{}".format(day.strftime("%d-%m-%y"),
                                     destination.station_id, origin.station_id)
        if not os.path.isfile(filename):
          sleep(SLEEP_BETWEEN_REQUESTS_SECONDS)
          response = requests.get(url, headers={'User-Agent': USER_AGENT})
          try:
            json_value = json.loads(response.content)
          except:
            continue
          with open(filename, "w") as text_file:
            json.dump(json_value, text_file)
        else:
          with open(filename, "r") as text_file:
            json_value = json.load(text_file)

        # Load data from json
        if not json_value["LUZ"]["Directs"]:
          continue
        try:
          direct_list = json_value["LUZ"]["Directs"]["Direct"]
          for direct in direct_list:
            trip = parse_trip(direct["train"], origin, destination, stations_map)
            trips.append(trip)
        except:
          print 'Failed to parse trip from {} to {}'.format(origin.name, destination.name)

  return trips

def merge_trips(trips):
  """Merges all trips in given trip list, returning a map of train number to merged trip"""
  trip_map = {}
  for trip in trips:
    if trip.train_number not in trip_map:
      trip_map[trip.train_number] = [trip]
    else:
      trip_map[trip.train_number].append(trip)

  for key in trip_map:
    trip_map[key] = merge_single_train_trips(trip_map[key])
  return trip_map

def merge_single_train_trips(trips):
  """Merges all trips in given trip list (belonging to the same train), returning a merged trip"""
  if len(trips) == 0:
    return None
  if len(trips) == 1:
    return trips[0]
  # Set merged_trip to the first trip. We will then iteratively merge the rest of the trips into it
  merged_trip = trips[0]
  for trip_to_merge in trips[1::]:
    # Exclude the last stop from both trips since its departure is null and we can't sort it
    stops = merged_trip.stops[:-1] + trip_to_merge.stops[:-1]
    stops.sort(key=lambda x: x.departure)
    # Add the last stop from only one of the trips. Choose the one that the train arrives later to.
    if merged_trip.stops[-1].arrival > trip_to_merge.stops[-1].arrival:
      stops.append(merged_trip.stops[-1])
    else:
      stops.append(trip_to_merge.stops[-1])
    # Merge stops in new stop list new_stops.
    new_stops = []
    for stop in stops:
      if not new_stops:  # First stop is just added
        new_stops.append(stop)
      else:
        last_stop = new_stops[-1]
        # The stop and last_stop need to be merged if they're for the same station
        if last_stop.station.station_id == stop.station.station_id:
          # Sanity checks - arrivals and departures should be the same if defined
          assert not last_stop.arrival or not stop.arrival or last_stop.arrival == stop.arrival
          assert (not last_stop.departure or not stop.departure
                  or last_stop.departure == stop.departure)
          # Do the actual merge
          if not last_stop.arrival:
            last_stop.arrival = stop.arrival
          if not last_stop.departure:
            last_stop.departure = stop.departure
        else:  # Different stop, no merging, just adding
          new_stops.append(stop)
    merged_trip.stops = new_stops
  return merged_trip

if __name__ == "__main__":
  # Example run:
  query_day = datetime.datetime(2016, 5, 15, 8, 0, 0) # Can change to datetime.datetime.now()
  all_trips = get_trips_through_tel_aviv(query_day)
  merged_trips = merge_trips(all_trips)
  for trip_x in merged_trips.values():
    print trip_x
    for stop_x in trip_x.stops:
      print stop_x
    print
