import datetime

from . import chat_step


class TrainDateAndTimeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'train_date_and_time'

    def send_message(self):
        message = 'מתי הרכבת היתה אמורה לצאת?'
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        text = self._extract_text(messaging_event)
        # TODO: Accept several date formats, parse user's response or use a datepicker
        try:
            input_time = datetime.datetime.strptime(text, '%H:%M').time()
            approx_train_time = datetime.datetime.combine(datetime.datetime.now(), input_time)
        except ValueError:
            self._send_message('לא הצלחתי להבין את התשובה :( נסו לכתוב שעה כמו: 16:20')
            return self.get_name()

        self._set_step_data(approx_train_time.strftime(self.STORAGE_DATETIME_FORMAT), key='approx_train_time')

        return 'source_station'
