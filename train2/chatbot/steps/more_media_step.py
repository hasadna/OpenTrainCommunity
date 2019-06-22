import logging
from . import chat_step

logger = logging.getLogger(__name__)


class MoreMediaStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'more_media'

    def send_message(self):
        self._send_message('תודה. ניתן לשלוח עוד תמונות וסרטונים, או לסיים ע"י הודעת ביי')

    def handle_user_response(self, chat_data_wrapper):
        return 'more_media'

