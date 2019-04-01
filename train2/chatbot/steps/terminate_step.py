from . import chat_step


class TerminateStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'terminate'

    def send_message(self):
        message = ':('
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        pass
