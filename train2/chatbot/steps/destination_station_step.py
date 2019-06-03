import copy
import datetime

from . import chat_step
from chatbot.station_utils import StationUtils
from chatbot.chat_utils import ChatUtils
from common.ot_gtfs_utils import get_trips_from_to


class DestinationStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'destination_station'

    def send_message(self):
        previous_response = ChatUtils.get_response_to_step(self.session, self.get_name())
        if previous_response:
            text = self._extract_text(previous_response)
            matching_stations = StationUtils.find_matching_stations(text)
            if 2 <= len(matching_stations) <= self.MAX_ITEMS_FOR_SUGGESTIONS:
                message = 'איזו מאלה?'
                suggestions = []
                for station in matching_stations:
                    station_name = station.main_name
                    suggestions.append({
                        'text': station_name,
                        'payload': station_name,
                    })
                self._send_suggestions(message, suggestions)
                return

            self._send_message('אני לא כל כך בטוח איזו תחנה זו, אולי ננסה משהו יותר ספציפי?')
            return

        self._send_message('ולאיזו תחנה?')

    def handle_user_response(self, messaging_event):
        text = self._extract_text(messaging_event)
        matching_stations = StationUtils.find_matching_stations(text)

        if len(matching_stations) == 0:
            self._send_message('האמת שאני לא מכיר תחנה כזאת...')
            return self.get_name()

        if 2 <= len(matching_stations) <= self.MAX_ITEMS_FOR_SUGGESTIONS:
            return self.get_name()

        if len(matching_stations) > self.MAX_ITEMS_FOR_SUGGESTIONS:
            self._send_message('אני לא כל כך בטוח איזו תחנה זו, אולי ננסה משהו יותר ספציפי?')
            return self.get_name()

        station = matching_stations[0]
        station_name = station.main_name
        self._set_step_data(station.gtfs_code)
        self._send_message(station_name + ' 👍')

        return self._handle_chosen_destination_station()

    def _handle_chosen_destination_station(self):
        source_station_gtfs_code = ChatUtils.get_step_data(self.session, 'source_station')
        destination_station_gtfs_code = ChatUtils.get_step_data(self.session, 'destination_station')
        approx_train_time_str = ChatUtils.get_step_data(self.session, 'approx_train_time')
        approx_train_time = datetime.datetime.strptime(approx_train_time_str, self.STORAGE_DATETIME_FORMAT)

        trips = get_trips_from_to(
            from_code=source_station_gtfs_code,
            to_code=destination_station_gtfs_code,
            when=approx_train_time
        )

        if len(trips) == 0:
            self._send_message('לא מצאתי רכבת מתאימה :( ננסה שוב')
            return 'train_date_and_time'

        if 2 <= len(trips):
            nearest_trips = self.get_nearest_trips_by_departure_time(trips, number_of_trips=self.MAX_ITEMS_FOR_BUTTONS)
            serialized_trips = [self._serialize_trip(trip) for trip in nearest_trips]
            self._set_step_data(serialized_trips, key='potential_train_trips')
            return 'select_train_line'

        trip = trips[0]
        self._set_step_data(self._serialize_trip(trip), key='train_trip')
        description = self._get_trip_description(trip)
        self._send_message(description + ' 👍')
        return 'goodbye'

    def get_nearest_trips_by_departure_time(self, trips, number_of_trips=3):
        now = datetime.datetime.now()
        trips.sort(key=lambda x: self._get_timedelta(now, x['from']['departure_time']))
        return trips[:number_of_trips]

    @staticmethod
    def _get_timedelta(now, trip_time):
        if now.time() > trip_time:
            return now - datetime.datetime.combine(date=now.date(), time=trip_time)
        else:
            return datetime.datetime.combine(date=now.date(), time=trip_time) - now

    @staticmethod
    def _get_trip_description(trip):
        station_code = trip['from']['stop_code']
        station = StationUtils.get_station_by_code(station_code)
        if station is None:
            source_station = trip['from']['stop_name']
        else:
            source_station = station.main_name
        departure_time = trip['from']['departure_time'].strftime('%H:%M')
        return f"{departure_time} מ{source_station}"

