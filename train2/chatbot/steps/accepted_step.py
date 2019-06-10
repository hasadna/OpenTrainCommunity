import logging

import requests
from django.conf import settings

from chatbot import models
from chatbot.chat_utils import ChatUtils
from common.ot_gtfs_utils import get_full_trip
from . import chat_step

logger = logging.getLogger(__name__)


class AcceptedStep(chat_step.ChatStep):
    @staticmethod
    def get_name():
        return 'accepted'

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

        full_user_data = self.get_full_user_data()

        chat_report = models.ChatReport.objects.create(
            report_type=models.ChatReport.ReportType.CANCEL,
            session=self.session,
            full_trip=full_reported_trip,
            user_data=full_user_data)
        logger.info("Created chat report %d", chat_report.id)

    def get_full_user_data(self):
        url = f"https://graph.facebook.com/{self.session.user_id}"
        params = {
            'fields': 'first_name,last_name,profile_pic',
            'access_token': settings.FB_PAGE_ACCESS_TOKEN
        }
        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as ex:
            logger.error('failed to get user data: %s', ex)
            return {
                'user_id': self.session.user_id,
                'error': str(ex)
            }
