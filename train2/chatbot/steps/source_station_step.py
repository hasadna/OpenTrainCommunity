from . import chat_step
from ..station_utils import StationUtils
from ..chat_utils import ChatUtils


class SourceStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'source_station'

    def send_message(self):
        text = ChatUtils.get_step_data(self.session, self.get_prev_result_key())
        if text:
            matching_stations = StationUtils.find_matching_stations(text)
            if 2 <= len(matching_stations) <= self.MAX_ITEMS_FOR_SUGGESTIONS:
                message = 'איזו מאלה?'
                suggestions = []
                for station in matching_stations:
                    suggestions.append({
                        'text': station.main_name,
                        'payload': station.id,
                    })
                self._send_suggestions(message, suggestions)
                return

            self._send_message('אני לא כל כך בטוח איזו תחנה זו, אולי ננסה משהו יותר ספציפי?')
            return

        self._send_message('מאיזו תחנה?')

    def handle_user_response(self, chat_data_wrapper):
        if chat_data_wrapper.is_quick_reply():
            station_id = chat_data_wrapper.extract_selected_quick_reply()
            matching_station = StationUtils.get_station_by_id(station_id=station_id)
            matching_stations = [matching_station] if matching_station else []
        else:
            text = chat_data_wrapper.extract_text()
            self._set_step_data(text, key=self.get_prev_result_key())
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
        return 'destination_station'
