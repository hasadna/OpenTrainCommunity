from . import chat_step
from chatbot.chat_utils import ChatUtils
from chatbot.station_utils import StationUtils


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

    def handle_user_response(self, chat_data_wrapper):
        potential_trips = ChatUtils.get_step_data(self.session, 'potential_train_trips')
        potential_trips = [self._deserialize_trip(trip) for trip in potential_trips]
        print('***')
        print(potential_trips)

        selected_trip_index = chat_data_wrapper.extract_selected_quick_reply()

        if selected_trip_index is None:
            return self.get_name()

        trip = potential_trips[int(selected_trip_index)]

        self._set_step_data(self._serialize_trip(trip), key='train_trip')

        description = self._get_trip_description(trip)
        self._send_message(description + ' 👍')

        return 'accepted'

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
