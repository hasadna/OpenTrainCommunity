from . import chat_step


class SourceStationStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'source_station'

    def send_message(self):
        message = 'באיזו תחנה?'
        # TODO: Send possible stations
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        # TODO: Parse station and use a station_id
        # text = self._extract_text(messaging_event)
        # self.session.source_train_station = text
        # self.session.save()

        return 'destination_station'
