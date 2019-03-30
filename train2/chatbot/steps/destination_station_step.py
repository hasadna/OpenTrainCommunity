from . import chat_step
from chatbot.station_utils import StationUtils
from chatbot.chat_utils import ChatUtils


class DestinationStationStep(chat_step.ChatStep):
    MAX_STATIONS_FOR_SUGGESTIONS = 6

    @staticmethod
    def get_name():
        return 'destination_station'

    def send_message(self):
        previous_response = ChatUtils.get_response_to_step(self.session, self.get_name())
        if previous_response:
            text = self._extract_text(previous_response)
            matching_stations = StationUtils.find_matching_stations(text)
            if 2 <= len(matching_stations) <= self.MAX_STATIONS_FOR_SUGGESTIONS:
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

        if 2 <= len(matching_stations) <= self.MAX_STATIONS_FOR_SUGGESTIONS:
            return self.get_name()

        if len(matching_stations) > self.MAX_STATIONS_FOR_SUGGESTIONS:
            self._send_message('אני לא כל כך בטוח איזו תחנה זו, אולי ננסה משהו יותר ספציפי?')
            return self.get_name()

        station = matching_stations[0]
        station_name = station.main_name
        self._send_message(station_name + ' 👍')
        # return 'select_train_line'
        return 'goodbye'
