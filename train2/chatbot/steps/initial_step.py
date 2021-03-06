from . import chat_step


class InitialStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'initial'

    def send_message(self):
        pass

    def handle_user_response(self, chat_data_wrapper):
        self._send_message('היי!')
        self._send_message('אני בוט שמאפשר לדווח על רכבות שבוטלו')
        self._send_message('בכל שלב אפשר להתחיל מהתחלה ע"י שליחת ההודעה "ביי"')
        return 'welcome'
