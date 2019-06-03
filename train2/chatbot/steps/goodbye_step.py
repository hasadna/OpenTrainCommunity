import logging

from chatbot import models
from chatbot.chat_utils import ChatUtils
from . import chat_step

logger = logging.getLogger(__name__)

class GoodbyeStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'goodbye'

    def send_message(self):
        self.save_chat_report()

        message = 'קיבלתי 👍 תודה רבה על הדיווח, אני מקווה שתצליחו להגיע ליעד בקרוב... :)'
        self._send_message(message)

    def handle_user_response(self, messaging_event):
        return 'restart'

    def save_chat_report(self):
        reported_trip = ChatUtils.get_step_data(self.session, 'train_trip')
        chat_report = models.ChatReport.objects.create(
            report_type=models.ChatReport.ReportType.CANCEL,
            session=self.session,
            full_trip=reported_trip,
            user_data=self.session.user_id)
        logger.info("Created chat report %d", chat_report.id)

