import random

from chatbot.bot_wrapper import BotButton
from . import chat_step


class WelcomeStep(chat_step.ChatStep):
    SYMPATHETIC_MESSAGES = [
        'אוי אני שונא כשזה קורה...',
        'עצוב לי לשמוע...',
        'איזה מרגיז...',
    ]
    BUTTON_REPORT_CANCELED_TRAIN = 'button_report_canceled_train'
    BUTTON_CANCEL = 'button_cancel'

    @staticmethod
    def get_name():
        return 'welcome'

    def send_message(self):
        message = 'תרצו לדווח על רכבת שבוטלה?'
        buttons = [
            BotButton(title='כן', payload=self.BUTTON_REPORT_CANCELED_TRAIN),
            BotButton(title='לא', payload=self.BUTTON_CANCEL)
        ]
        self._send_buttons(message, buttons)

    def handle_user_response(self, chat_data_wrapper):
        text = chat_data_wrapper.extract_text()
        button_payload = chat_data_wrapper.extract_selected_button()
        if button_payload != self.BUTTON_REPORT_CANCELED_TRAIN and text != 'כן':
            self._send_message('אוקי, אני אחכה פה עד שתתבטל רכבת...')
            return 'restart'

        sympathetic_message = random.choice(self.SYMPATHETIC_MESSAGES)
        self._send_message(sympathetic_message)
        return 'train_time_approx_now'
