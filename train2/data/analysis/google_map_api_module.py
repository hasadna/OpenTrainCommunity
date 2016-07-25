import numpy as np
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='mykey')



# Return the driving trip duration in minutes
def get_trip_duration(start, end, duration):
    dirs = gmaps.directions(start, end, departure_time=departure_time, mode='driving')
    duration = dirs[0]['legs'][0]['duration']['value'] / 60.0
    duration_traffic = dirs[0]['legs'][0]['duration_in_traffic']['value'] / 60.0

    return duration, duration_traffic


if __name__ == '__main__':
    start = 'Rehovot,  Israel'
    end = 'Tel Aviv, Israel'
    departure_time = datetime(2016, 7, 21, 9, 00)

    duration, duration_traffic = get_trip_duration(start, end, departure_time)

    print('Duration from %s to %s will take %0.0f minutes.' %(start, end, duration))
    print('Duration in Traffic from %s to %s on %s will take %0.0f minutes.' %(start, end, departure_time, duration_traffic))