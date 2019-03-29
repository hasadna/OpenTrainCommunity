from . import chat_step


class InitialStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'initial'

    def send_message(self):
        pass

    def handle_user_response(self, user_response):
        return 'welcome'
