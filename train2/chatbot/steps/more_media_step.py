import logging
from . import chat_step

logger = logging.getLogger(__name__)


class MoreMediaStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'more_media'

    def send_message(self):
        self._send_message('תודה. באפשרותך לשלוח תמונה או סרטון נוסף. ניתן לסיים ע"י שליחת הודעה כל טקסט')

    def handle_user_response(self, messaging_event):
        atts = self._extract_attachments(messaging_event)
        if atts:
            self.session.report.attachments.extend(atts)
            self.session.report.save()
            return 'more_media'
        return 'terminate'

