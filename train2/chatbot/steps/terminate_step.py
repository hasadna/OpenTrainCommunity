from . import chat_step


class TerminateStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'terminate'

    def send_message(self):
        if getattr(self.session, 'report', None):
            message = '\u263a'
        else:
            message = '\u2639'
        self._send_message(message)

    def handle_user_response(self, chat_data_wrapper):
        pass
