from . import chat_step


class GoodbyeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'goodbye'

    def send_message(self):
        message = 'קיבלתי 👍 תודה רבה על הדיווח, אני מקווה שתצליחו להגיע ליעד בקרוב... :)'
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        return 'restart'
