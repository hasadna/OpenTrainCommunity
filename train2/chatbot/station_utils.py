import re
import Levenshtein

from data.models import Stop


class StationUtils:
    @classmethod
    def find_matching_stations(cls, text):
        matching_stations = []
        all_stops = Stop.objects.all()

        for stop in all_stops:
            for name in stop.hebrew_list:
                if cls._is_exact_match(text, name):
                    return [stop]

                if cls._is_text_matches_station(text, name):
                    matching_stations.append(stop)
                    # We break from the inner loop so that if we get a match
                    # for 2 different names of a station, we don't return it twice
                    break

        return matching_stations

    @classmethod
    def get_station_by_id(cls, station_id):
        try:
            return Stop.objects.get(id=station_id)
        except Stop.DoesNotExist:
            return None

    @classmethod
    def get_station_by_code(cls, gtfs_code):
        try:
            return Stop.objects.get(gtfs_code=gtfs_code)
        except Stop.DoesNotExist:
            return None

    @classmethod
    def _is_exact_match(cls, text, station_name):
        normalized_text = cls._normalize(text)
        normalized_station_name = cls._normalize(station_name)

        return normalized_text == normalized_station_name

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
