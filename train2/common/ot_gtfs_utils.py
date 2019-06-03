import logging
import datetime
import shutil
import urllib.request
import os
import subprocess
import pandas as pd
from . import obus_gtfs_utils


logger = logging.getLogger(__name__)


def get_workdir(date):
    base_dir = os.path.join(os.path.dirname(__file__), 'gtfs_workdir')
    path = os.path.join(base_dir, date.isoformat())
    os.makedirs(path, exist_ok=True)
    return path


def create_train_gtfs(gtfs_file, train_gtfs_file):
    workdir = os.path.dirname(gtfs_file)
    unzip_dir = os.path.join(workdir, 'unzip-folder')

    def p(f):
        return os.path.join(unzip_dir, f)

    if os.path.exists(unzip_dir):
        shutil.rmtree(unzip_dir)
    os.makedirs(unzip_dir, exist_ok=False)
    subprocess.check_call(['unzip', gtfs_file, '-d', unzip_dir])
    os.rename(p('stop_times.txt'), p('stop_times_old.txt'))

    logger.info("unzip dir = %s", unzip_dir)
    trips = pd.read_csv(p('trips.txt'))
    routes = pd.read_csv(p('routes.txt'))
    trip_with_routes = trips.merge(routes, on='route_id').query('agency_id=="2"')
    trip_ids = frozenset(trip_with_routes.trip_id)
    with open(p('stop_times.txt'), 'w') as fw:
        with open(p('stop_times_old.txt')) as fr:
            header = True
            for line in fr:
                if header:
                    fw.write(line + '\n')
                    header = False
                trip_id = line.partition(",")[0]
                if trip_id in trip_ids:
                    fw.write(line + '\n')
    logger.info('Wrote new %s', p('stop_times.txt'))
    os.unlink(p('stop_times_old.txt'))
    os.unlink(p('shapes.txt'))
    os.unlink(p('fare_rules.txt'))
    if os.path.exists(train_gtfs_file):
        os.unlink(train_gtfs_file)
    subprocess.check_call(f'zip {train_gtfs_file} *.txt', cwd=unzip_dir, shell=True)
    logger.info('Wrote %s', train_gtfs_file)
    return train_gtfs_file


def get_train_gtfs(date: datetime.date = None, force: bool = False) -> str:
    date = date or datetime.date.today()
    gtfs_file = os.path.join(get_workdir(date), f'{date.isoformat()}.zip')
    if force or not os.path.exists(gtfs_file):
        url = f'https://s3-eu-west-1.amazonaws.com/s3.obus.hasadna.org.il/{date.isoformat()}.zip'
        logger.info('Downloading %s', url)
        urllib.request.urlretrieve(url, gtfs_file)
        logger.info(f"Downloaded to %s", gtfs_file)
    else:
        logger.info(f"Already downloaded %s", gtfs_file)
    train_gtfs_file = os.path.join(get_workdir(date), f'{date.isoformat()}_train.zip')
    if not os.path.exists(train_gtfs_file):
        create_train_gtfs(gtfs_file, train_gtfs_file)
    return train_gtfs_file


def build_pickle_old(date: datetime.date, pickle_file: str) -> str:
    json_file = pickle_file.replace(".pickle", ".json")
    daily_gtfs = get_train_gtfs(date)
    feed = obus_gtfs_utils.get_partridge_feed_by_date(daily_gtfs, date)
    trips_and_routes = feed.trips.merge(feed.routes, on="route_id")
    #train_trips_and_routes = trips_and_routes[trips_and_routes['agency_id']=='2']
    train_trips_and_routes = trips_and_routes.query('agency_id=="2"')
    train_stops_trip_routes = feed.stop_times.merge(train_trips_and_routes, on="trip_id")
    latest_train_data = train_stops_trip_routes.merge(feed.calendar, on="service_id")
    stop_ids = latest_train_data['stop_id'].unique()
    train_stops = feed.stops[feed.stops.stop_id.isin(stop_ids)]
    latest_train_data_with_stops = latest_train_data.merge(train_stops, on="stop_id")
    latest_train_data_with_stops.to_pickle(pickle_file)
    latest_train_data_with_stops.to_json(json_file)
    return pickle_file


def get_train_trip_ids(feed):
    trips_compact = feed.trips[['trip_id', 'route_id']]
    train_trips_and_routes_compact = trips_compact.merge(feed.routes, on='route_id').query('agency_id=="2"')
    return train_trips_and_routes_compact.trip_id


def get_feed(date):
    daily_gtfs = get_train_gtfs(date)
    logger.info("getting partidige feed")
    feed = obus_gtfs_utils.get_partridge_feed_by_date(daily_gtfs, date)
    logger.info("feed is built")
    return feed


def build_pickle(date: datetime.date, pickle_file: str) -> str:
    json_file = pickle_file.replace(".pickle", ".json")
    # extract train trip ids
    feed = get_feed(date)
    trip_ids = get_train_trip_ids(feed)
    train_trips = feed.trips[feed.trips.trip_id.isin(trip_ids)]
    train_trips_routes = train_trips.merge(feed.routes, on='route_id')
    # this is the most expensive call
    # since we need to read all the stop times
    train_stop_times = feed.stop_times[feed.stop_times.trip_id.isin(trip_ids)]

    train_stops_trip_routes = train_stop_times.merge(train_trips_routes, on="trip_id")
    latest_train_data = train_stops_trip_routes.merge(feed.calendar, on="service_id")
    stop_ids = latest_train_data['stop_id'].unique()
    train_stops = feed.stops[feed.stops.stop_id.isin(stop_ids)]
    latest_train_data_with_stops = latest_train_data.merge(train_stops, on="stop_id")
    latest_train_data_with_stops.to_pickle(pickle_file)
    latest_train_data_with_stops.to_json(json_file)
    return pickle_file


def get_or_create_daily_trips(date: datetime.date = None, force: bool = False, add_pickle_path: bool = False) -> pd.DataFrame:
    date = date or datetime.date.today()
    pickle_file = os.path.join(get_workdir(date), f"{date.isoformat()}.pickle")
    if not os.path.exists(pickle_file) or force:
        logger.info(f"No pickle {pickle_file}, will download and build")
        build_pickle(date, pickle_file)
    logger.info(f"Return from pickle {pickle_file}")
    df = pd.read_pickle(pickle_file)
    if not add_pickle_path:
        return df
    return df, pickle_file

def get_trips_from_to(from_code: str, to_code: str, when: datetime.datetime = None):
    """ Searches daily GTFS data (Pandas DataFrame) for trips
    :param when: Timestamp around which to search +- 1 hour
    :param from_code, to_code: Station code from GTFS data (different from GTFS id stored in db)
    :return: array of results
    """
    when = when or datetime.datetime.now()
    date = when.date()
    df, pickle_path = get_or_create_daily_trips(date, add_pickle_path=True)
    stops_departure = df[df.stop_code == from_code]
    stops_arrival = df[df.stop_code == to_code]
    merge_stops = stops_departure.merge(stops_arrival, on="trip_id")
    daily_stops_from_to = merge_stops[merge_stops.stop_sequence_y > merge_stops.stop_sequence_x]
    time_since_midnight = 3600 * when.hour + 60 * when.minute + when.second
    start_seconds = time_since_midnight - 3600
    end_seconds = time_since_midnight + 3600
    delta_stops_from_to = daily_stops_from_to[(daily_stops_from_to.departure_time_x > start_seconds) & (daily_stops_from_to.departure_time_x < end_seconds)]
    delta_stops_from_to_sorted = delta_stops_from_to.sort_values('departure_time_x')

    results = [{
        'from':
            {
                'stop_code': row.stop_code_x,
                'stop_name': row.stop_name_x,
                'departure_time': midnight_sec_to_time(row.departure_time_x)
            },
        'to':
            {
                'stop_code': row.stop_code_y,
                'stop_name': row.stop_name_y,
                'departure_time': midnight_sec_to_time(row.departure_time_y)
            },
        'trip':
            {
                'description': row.route_long_name_x,
                'route_id': row.route_id_x,
                'trip_id': row.trip_id,
                'pickle_path': pickle_path
            },
    } for idx, row in delta_stops_from_to_sorted.iterrows()]

    logger.info('gtfs: get_trips_from_to: {}'.format(results))
    return results


def get_stops(date=None):
    date = date or datetime.date.today()
    df = get_or_create_daily_trips(date)
    df_stops = df[['stop_code', 'stop_name']].drop_duplicates().sort_values('stop_name')
    return [{
        'stop_code': row.stop_code,
        'stop_name': row.stop_name
    } for idx, row in df_stops.iterrows()]


def midnight_sec_to_time(seconds):
    datetime_since_midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=seconds)
    return datetime_since_midnight.time()
