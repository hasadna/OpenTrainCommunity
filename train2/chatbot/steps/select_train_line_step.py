import copy
import datetime

from . import chat_step
from chatbot.chat_utils import ChatUtils


class SelectTrainLineStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'select_train_line'

    def send_message(self):
        potential_trips = ChatUtils.get_step_data(self.session, 'potential_train_trips')

        potential_trips = [self._deserialize_trip(trip) for trip in potential_trips]

        message = 'איזו מאלה?'
        suggestions = []
        for index, trip in enumerate(potential_trips):
            print('###')
            print(index)
            trip_description = self._get_trip_description(trip)
            suggestions.append({
                "type": "postback",
                "text": trip_description,
                "payload": index,
            })

        self._send_suggestions(message, suggestions)

    def handle_user_response(self, messaging_event):
        potential_trips = ChatUtils.get_step_data(self.session, 'potential_train_trips')
        potential_trips = [self._deserialize_trip(trip) for trip in potential_trips]
        print('***')
        print(potential_trips)

        selected_trip_index = self._extract_selected_quick_reply(messaging_event)

        if selected_trip_index is None:
            return self.get_name()

        trip = potential_trips[int(selected_trip_index)]

        self._set_step_data(self._serialize_trip(trip), key='train_trip')

        description = self._get_trip_description(trip)
        self._send_message(description + ' 👍')

        return 'goodbye'

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

    @staticmethod
    def _serialize_trip(trip):
        serialized_trip = copy.deepcopy(trip)
        serialized_trip['from']['departure_time'] = serialized_trip['from']['departure_time'].strftime('%H%M')
        serialized_trip['to']['departure_time'] = serialized_trip['to']['departure_time'].strftime('%H%M')
        return serialized_trip

    @staticmethod
    def _deserialize_trip(trip):
        deserialized_trip = copy.deepcopy(trip)
        deserialized_trip['from']['departure_time'] = datetime.datetime.strptime(deserialized_trip['from']['departure_time'], '%H%M').time()
        deserialized_trip['to']['departure_time'] = datetime.datetime.strptime(deserialized_trip['to']['departure_time'], '%H%M').time()
        return deserialized_trip
