from enum import Enum

from django.test import TestCase
from django.urls import reverse

import data.stop_utils
from django.utils.translation import activate
import data.importer
import datetime

from django.conf import settings
from . import models
import functools
import pytz


class Stops(Enum):
    TA_HAGANA = 4900
    TA_HASHALOM = 4600
    TA_MERKAZ = 3700
    TA_UNIV = 3600
    BINYAMINA = 2800
    ATLIT = 2500
    HAIFA_HOF_CARMEL = 2300


class DataIntegrityTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        activate(settings.LANGUAGE_CODE)
        data.stop_utils.build_stops()

    def test_trip_in_correct_time_and_day_slot(self):

        tz = pytz.timezone(zone='Asia/Jerusalem')
        today = datetime.date.today()
        trip = data.importer.create_trip(train_num=1, date=today)
        stops = [Stops.TA_HAGANA, Stops.TA_HASHALOM, Stops.TA_MERKAZ, Stops.TA_UNIV, Stops.BINYAMINA, Stops.ATLIT,
                 Stops.HAIFA_HOF_CARMEL]
        trip_start_time = tz.localize(datetime.datetime(year=today.year, month=today.month, day=today.day,
                                                        hour=9, minute=40))

        for idx, stop_enum in enumerate(stops, start=1):
            stop = stop_enum.value
            data.importer.create_sample(trip=trip,
                                        is_source=idx == 1,
                                        is_dest=idx == len(stops),
                                        gtfs_stop_id=stop,
                                        gtfs_stop_name=get_stop_name(stop),
                                        exp_arrival=trip_start_time + datetime.timedelta(minutes=10 * idx),
                                        actual_arrival=trip_start_time + datetime.timedelta(minutes=10 * idx),
                                        exp_departure=trip_start_time + datetime.timedelta(minutes=(10 * idx) + 1),
                                        actual_departure=trip_start_time + datetime.timedelta(minutes=(10 * idx) + 1),
                                        index=idx,
                                        filename='test_data',
                                        sheet_idx=0,
                                        line_number=idx,
                                        valid=True,
                                        invalid_reason=None)

        trip.complete_trip()

        resp = self.client.get(reverse('stats-route-info-full'), {'route_id': trip.route_id})
        json = resp.json()

        day_hour =  self.get_elements_matching(json, week_day=2, hour=9)
        day_hour_all = self.get_elements_matching(json, week_day=2, hour='all')

        day_all_hour =  self.get_elements_matching(json, week_day='all', hour=9)
        day_all_hour_all =  self.get_elements_matching(json, week_day='all', hour='all')
        for slot in (day_hour, day_hour_all, day_all_hour, day_all_hour_all):
            self.assertEqual(len(slot), 1, msg="One trip expected in the slot!")

    def get_elements_matching(self, json, week_day, hour):
        list_of_elements = []
        for element in json:
            el_week_day = element['info']['week_day']
            el_hours_list = element['info']['hours']
            if el_week_day == week_day and self._hour_within_range(hour, el_hours_list):
                list_of_elements.append(element)
        return list_of_elements

    @staticmethod
    def _hour_within_range(hour, hours_list):
        if hour == 'all' or hours_list == 'all':
            if hours_list == hour:
                return True
        else:
            start = hours_list[0] % 24
            end = hours_list[1] % 24
            if start <= hour < end:
                return True

        return False


    def test_trip_has_correct_late_arrival_pct(self):
        pass

    def test_path_with_several_trips_has_correct_totals(self):
        pass


@functools.lru_cache(maxsize=100)
def get_stop_name(gtfs_id):
    return models.Stop.objects.get(gtfs_stop_id=gtfs_id).main_name
