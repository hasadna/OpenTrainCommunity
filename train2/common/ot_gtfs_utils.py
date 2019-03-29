import datetime
import urllib.request
import tempfile
import os
import pandas as pd
from . import obus_gtfs_utils


def get_workdir(date):
    path = os.path.join(tempfile.gettempdir(), date.isoformat())
    os.makedirs(path, exist_ok=True)
    return path


def download_daily_gtfs(date: datetime.date = None, force: bool = False) -> str:
    date = date or datetime.date.today()
    tmpfile = os.path.join(get_workdir(date), f'{date.isoformat()}.zip')
    if force or not os.path.exists(tmpfile):
        url = f'https://s3-eu-west-1.amazonaws.com/s3.obus.hasadna.org.il/{date.isoformat()}.zip'
        tmpfile = os.path.join(get_workdir(date), f'{date.isoformat()}.zip')
        urllib.request.urlretrieve(url, tmpfile)
        print(f"Downloaded to {tmpfile}")
    else:
        print(f"Already downloaded f{tmpfile}")
    return tmpfile


def build_pickle(date: datetime.date, pickle_file: str) -> str:
    daily_gtfs = download_daily_gtfs(date)
    feed = obus_gtfs_utils.get_partridge_feed_by_date(daily_gtfs, date)
    trips_and_routes = feed.trips.merge(feed.routes, on="route_id")
    train_trips_and_routes = trips_and_routes[trips_and_routes['agency_id']=='2']
    train_stops_trip_routes = feed.stop_times.merge(train_trips_and_routes, on="trip_id")
    latest_train_data = train_stops_trip_routes.merge(feed.calendar, on="service_id")
    stop_ids = latest_train_data['stop_id'].unique()
    train_stops = feed.stops[feed.stops.stop_id.isin(stop_ids)]
    latest_train_data_with_stops = latest_train_data.merge(train_stops, on="stop_id")
    latest_train_data_with_stops.to_pickle(pickle_file)
    return pickle_file


def get_or_create_daily_trips(date: datetime.date = None, force:bool = False) -> pd.DataFrame:
    date = date or datetime.date.today()
    pickle_file = os.path.join(get_workdir(date),f"{date.isoformat()}.pickle")
    if not os.path.exists(pickle_file) or force:
        print(f"Building pickle {pickle_file}")
        build_pickle(date, pickle_file)
    print(f"Return from pickle {pickle_file}")
    return pd.read_pickle(pickle_file)


def get_trips_from_to(from_code: str, to_code: str, when: datetime.datetime = None):
    """
    :param when:
    :param from_code:
    :param to_code:
    :return:
    """
    when = when or datetime.datetime.now()
    date = when.date()
    df = get_or_create_daily_trips(date)
    stops_departure = df[df.stop_code == from_code]
    stops_arrival = df[df.stop_code == to_code]
    merge_stops = stops_departure.merge(stops_arrival, on="trip_id")
    daily_stops_from_to = merge_stops[merge_stops.stop_sequence_y > merge_stops.stop_sequence_x]
    time_since_midnight = 3600 * when.hour + 60 * when.minute + when.second
    start_seconds = time_since_midnight - 3600
    end_seconds = time_since_midnight + 3600
    delta_stops_from_to = daily_stops_from_to[(daily_stops_from_to.departure_time_x > start_seconds) & (daily_stops_from_to.departure_time_x < end_seconds)]
    delta_stops_from_to_sorted = delta_stops_from_to.sort_values('departure_time_x')

    return [{
        'from':
            {
                'stop_code': row.stop_code_x,
                'stop_name': row.stop_name_x,
                'departure_time' : midnight_sec_to_time(row.departure_time_x)
            },
        'to':
            {
                'stop_code': row.stop_code_y,
                'stop_name': row.stop_name_y,
                'departure_time': midnight_sec_to_time(row.departure_time_y)
            },
        'route':
            {
                'description': row.route_long_name_x
            }
    } for idx, row in delta_stops_from_to_sorted.iterrows()]


def get_stops():
    df = get_or_create_daily_trips()
    df_stops = df[['stop_code', 'stop_name']].drop_duplicates().sort_values('stop_name')
    return [{
        'stop_code': row.stop_code,
        'stop_name': row.stop_name
    } for idx, row in df_stops.iterrows()]


def midnight_sec_to_time(seconds):
    datetime_since_midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=seconds)
    return datetime_since_midnight.time().isoformat()



