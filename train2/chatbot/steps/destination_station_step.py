from . import chat_step


class DestinationStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'destination_station'

    def send_message(self):
        message = 'ולאיזו תחנה?'
        # TODO: Send possible stations
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        # TODO: Parse station and use a station_id

        # return 'select_train_line'
        return 'goodbye'
