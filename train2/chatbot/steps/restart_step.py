from . import chat_step


class RestartStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'restart'

    def send_message(self):
        pass

    def handle_user_response(self, chat_data_wrapper):
        self._send_message('היי שוב!')
        return 'welcome'
