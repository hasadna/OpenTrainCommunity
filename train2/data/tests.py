import random
from enum import Enum

from hypothesis import given
from hypothesis.extra.django import TestCase
import hypothesis.strategies as st
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

    @given(st.dates(min_value=datetime.date(2015, 1, 1), max_value=datetime.date(2050, 1, 1)),
           st.integers(min_value=0, max_value=23),
           st.integers(min_value=0, max_value=59))
    def test_trip_in_correct_time_and_day_slot(self, trip_start_date, hour, minute):
        """
            Builds a trip with a constant number of ontime samples (stops), then queries django to verify
            the json response of the stats-route-info-full contains a single trip in the expected four slots.
        """
        tz = pytz.timezone(zone='Asia/Jerusalem')
        stops = [Stops.TA_HAGANA, Stops.TA_HASHALOM, Stops.TA_MERKAZ, Stops.TA_UNIV, Stops.BINYAMINA, Stops.ATLIT,
                 Stops.HAIFA_HOF_CARMEL]
        train_number = 1

        trip_weekday = self.get_israeli_weekday(trip_start_date)
        trip = data.importer.create_trip(train_num=train_number, date=trip_start_date)
        trip_start_time = tz.localize(datetime.datetime(year=trip_start_date.year, month=trip_start_date.month,
                                                        day=trip_start_date.day, hour=hour, minute=minute))

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

        day_hour =  self.get_elements_matching(json, week_day=trip_weekday, hour=hour)
        day_hour_all = self.get_elements_matching(json, week_day=trip_weekday, hour='all')

        day_all_hour =  self.get_elements_matching(json, week_day='all', hour=hour)
        day_all_hour_all =  self.get_elements_matching(json, week_day='all', hour='all')
        for slot in (day_hour, day_hour_all, day_all_hour, day_all_hour_all):
            self.assertEqual(len(slot), 1, msg=f"One trip expected in the slot! Actual json: {slot}")

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
            end = hours_list[1] % 24 if hours_list[1] != 24 else hours_list[1]
            if start <= hour < end:
                return True

        return False

    @staticmethod
    def get_israeli_weekday(date):
        """
        :param date: A datetime.date object
        :return: int representing the range 1 (Sun) to 7 (Sat)
        """
        if date.isoweekday() == 7:
            # rotate Sunday to 1
            return 1
        else:
            return date.isoweekday() + 1

    def test_trip_has_correct_late_arrival_pct(self):
        pass

    def test_path_with_several_trips_has_correct_totals(self):
        pass


@functools.lru_cache(maxsize=100)
def get_stop_name(gtfs_id):
    return models.Stop.objects.get(gtfs_stop_id=gtfs_id).main_name
