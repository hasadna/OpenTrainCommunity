import datetime

from . import chat_step


class WelcomeStep(chat_step.ChatStep):
    BUTTON_TRAIN_APPROX_NOW = 'welcome_train_approx_now'
    BUTTON_TRAIN_NOT_APPROX_NOW = 'welcome_train_not_approx_now'

    @staticmethod
    def get_name():
        return 'welcome'

    def send_message(self):
        message = 'הי! אני בוט שמאפשר לדווח על ביטול רכבות.\n' \
                  'האם מדובר על רכבת שהיתה אמורה לצאת בערך עכשיו?'
        buttons = [
            {
                "type": "postback",
                "title": "כן",
                "payload": self.BUTTON_TRAIN_APPROX_NOW
            },
            {
                "type": "postback",
                "title": "לא",
                "payload": self.BUTTON_TRAIN_NOT_APPROX_NOW
            },
        ]
        self._send_buttons(message, buttons)

    def handle_user_response(self, messaging_event):
        button_payload = self._extract_selected_button(messaging_event)
        if button_payload == self.BUTTON_TRAIN_APPROX_NOW:
            # self.session.approx_train_time = datetime.datetime.now()
            # self.session.save()
            return 'source_station'

        return 'train_date_and_time'
