import random

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
            {
                "type": "postback",
                "title": "כן",
                "payload": self.BUTTON_REPORT_CANCELED_TRAIN
            },
            {
                "type": "postback",
                "title": "לא",
                "payload": self.BUTTON_CANCEL
            },
        ]
        self._send_buttons(message, buttons)

    def handle_user_response(self, messaging_event):
        text = self._extract_text(messaging_event)
        button_payload = self._extract_selected_button(messaging_event)
        if button_payload != self.BUTTON_REPORT_CANCELED_TRAIN and text != 'כן':
            self._send_message('אוקי, אני אחכה פה עד שתתבטל רכבת...')
            return 'restart'

        sympathetic_message = random.choice(self.SYMPATHETIC_MESSAGES)
        self._send_message(sympathetic_message)
        return 'train_time_approx_now'
