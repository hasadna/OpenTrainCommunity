import datetime

from . import chat_step


class WelcomeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'welcome'

    def send_message(self):
        message = 'הי! אני בוט שמאפשר לדווח על ביטול רכבות\n' \
                  'האם מדובר על רכבת סביב שעה מעכשיו?'
        self._send_message(message)

    def handle_user_response(self, user_response):
        if user_response == 'כן':
            self.session.approx_train_time = datetime.datetime.now()
            self.session.save()
            return 'source_station'

        return 'train_date_and_time'
