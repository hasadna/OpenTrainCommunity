import logging

from chatbot import models
from chatbot.chat_utils import ChatUtils
from common.ot_gtfs_utils import get_full_trip
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
        trip_id = reported_trip['trip']['trip_id']
        route_id = reported_trip['trip']['route_id']
        pickle_path = reported_trip['trip']['pickle_path']
        full_reported_trip = get_full_trip(pickle_path=pickle_path, route_id=route_id, trip_id=trip_id)

        chat_report = models.ChatReport.objects.create(
            report_type=models.ChatReport.ReportType.CANCEL,
            session=self.session,
            full_trip=full_reported_trip,
            user_data=self.session.user_id)
        logger.info("Created chat report %d", chat_report.id)

