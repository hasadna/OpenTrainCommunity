from . import chat_step


class GoodbyeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'goodbye'

    def send_message(self):
        message = 'תודה רבה על הדיווח ובהצלחה בהגעה ליעד... :)'
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        # TODO: Allow to report a new train
        return self.get_name()
