from . import chat_step


class DestinationStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'destination_station'

    def send_message(self):
        message = 'לאיזו תחנה?'
        # TODO: Send possible stations
        self._send_message(message)

    def handle_user_response(self, user_response):
        # TODO: Parse station and use a station_id
        self.session.destination_train_station = user_response
        self.session.save()

        # return 'select_train_line'
        return 'goodbye'
