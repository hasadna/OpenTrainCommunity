import re
import Levenshtein

from common import ot_gtfs_utils
from .station import Station


class StationUtils:
    @classmethod
    def find_matching_stations(cls, text):
        matching_stations = []
        all_stops = ot_gtfs_utils.get_stops()

        for stop in all_stops:
            hebrew_names = [stop['stop_name']]
            for name in hebrew_names:
                if cls._is_text_matches_station(text, name):
                    code = stop['stop_code']
                    station = Station(code=code, hebrew_names=[name])
                    matching_stations.append(station)

        return matching_stations

    @classmethod
    def _is_text_matches_station(cls, text, station_name):
        normalized_text = cls._normalize(text)
        normalized_station_name = cls._normalize(station_name)

        if normalized_text in normalized_station_name:
            return True

        if Levenshtein.distance(normalized_text, normalized_station_name) <= 2:
            return True

        return False

    @staticmethod
    def _normalize(text):
        result = text.strip()
        result = re.sub('[\s_-]+', ' ', result)
        return result
