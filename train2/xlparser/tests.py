import os
from django.test import TestCase
from django.conf import settings
import xlparser.utils_2015
import data.stop_utils
from django.utils.translation import activate
import data.models


class DataParsingTests(TestCase):

    def setUpClass(cls):
        activate(settings.LANGUAGE_CODE)
        data.stop_utils.build_stops()

    def test_parse_single_valid_trip(self):
        single_trip_xl = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data', 'single_trip.xls'))
        xlparser.utils_2015.parse_xl(single_trip_xl)
        self.assertEqual(data.models.Trip.objects.count(), 1)
        trip = data.models.Trip.objects.get()
        self.assertEqual(trip.samples.count(), 19)
        self.assertIs(trip.valid, True)

    def test_parse_single_invalid_trip(self):
        single_invalid_trip_xl = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data', 'single_invalid_trip.xls'))
        xlparser.utils_2015.parse_xl(single_invalid_trip_xl)
        self.assertEqual(data.models.Trip.objects.count(), 1)
        trip = data.models.Trip.objects.get()
        self.assertEqual(trip.samples.count(), 19)
        self.assertIs(trip.valid, False)
        self.assertRegexpMatches(trip.invalid_reason, 'different planned and stopped')


