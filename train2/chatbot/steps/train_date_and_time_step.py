import datetime

from . import chat_step


class TrainDateAndTimeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'train_date_and_time'

    def send_message(self):
        message = 'מתי היתה הרכבת שבוטלה?'
        self._send_message(message)

    def handle_user_response(self, user_response):
        # TODO: Accept several date formats, parse user's response or use a datepicker
        try:
            time_of_day = datetime.datetime.strptime(user_response, '%H:%M').time()
        except ValueError:
            self._send_message('לא הצלחתי להבין את התשובה :( נסו לכתוב שעה כמו: 16:42')
            return self.get_name()

        # self.session.approx_train_time = datetime.combine(datetime.date.today(), time_of_day)
        # self.session.save()

        return 'source_station'
