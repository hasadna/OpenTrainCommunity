from chatbot import constants
from chatbot.bot_wrapper import BotButton
from chatbot.chat_utils import ChatUtils
from . import chat_step


class ConfirmRetryStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'confirm_retry'

    def send_message(self):
        buttons = [
            BotButton(title='נו טוב מהתחלה', payload=constants.BUTTON_YES),
            BotButton(title='תודה, נוותר', payload=constants.BUTTON_NO)
        ]

        self._send_buttons(message='לא מצאתי רכבת מתאימה :( ננסה שוב?',
                           buttons=buttons)

    def handle_user_response(self, chat_data_wrapper):
        text = chat_data_wrapper.extract_text()
        button_payload = chat_data_wrapper.extract_selected_button()
        if button_payload != constants.BUTTON_YES:
            return 'terminate'
        else:
            ChatUtils.clear_step_data(self.session)
            return 'train_time_approx_now'

