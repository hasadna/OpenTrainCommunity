from . import chat_step


class SourceStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'source_station'

    def send_message(self):
        message = 'באיזו תחנה?'
        # TODO: Send possible stations
        self._send_message(message)

    def handle_user_response(self, user_response):
        # TODO: Parse station and use a station_id
        self.session.update(source_train_station=user_response)

        return 'destination_station'
