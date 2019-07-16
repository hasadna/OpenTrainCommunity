import datetime

from chatbot.bot_wrapper import BotButton
from . import chat_step


class TrainTimeApproxNowStep(chat_step.ChatStep):
    BUTTON_TRAIN_APPROX_NOW = 'welcome_train_approx_now'
    BUTTON_TRAIN_NOT_APPROX_NOW = 'welcome_train_not_approx_now'

    @staticmethod
    def get_name():
        return 'train_time_approx_now'

    def send_message(self):
        message = 'רכבת שהיתה אמורה לצאת בערך עכשיו?'
        buttons = [
            BotButton(title='כן', payload=self.BUTTON_TRAIN_APPROX_NOW),
            BotButton(title='לא', payload=self.BUTTON_TRAIN_NOT_APPROX_NOW)
        ]
        self._send_buttons(message, buttons)

    def handle_user_response(self, chat_data_wrapper):
        text = chat_data_wrapper.extract_text()
        button_payload = chat_data_wrapper.extract_selected_button()
        if button_payload == self.BUTTON_TRAIN_APPROX_NOW or text == 'כן':
            approx_train_time = datetime.datetime.now()
            self._set_step_data(approx_train_time.strftime(self.STORAGE_DATETIME_FORMAT), key='approx_train_time')
            return 'source_station'

        return 'train_date_and_time'
