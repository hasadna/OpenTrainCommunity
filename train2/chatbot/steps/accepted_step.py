import logging

import requests
from django.conf import settings

from chatbot import models, constants
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

        message = 'נוכל להשתמש בשם שלכם?'
        self._send_message(message)

        buttons = [
            BotButton(title='כן', payload=constants.BUTTON_YES),
            BotButton(title='לא', payload=constants.BUTTON_NO)
        ]
        self._send_buttons(message, buttons)


    def handle_user_response(self, chat_data_wrapper):
        text = chat_data_wrapper.extract_text()
        button_payload = chat_data_wrapper.extract_selected_button()
        if button_payload != constants.BUTTON_YES and text != 'כן':
            self._send_message('אוקי, לא נעלבתי...')
        else:
            self.save_user_info(chat_data_wrapper)

        self._send_message(
            'נשמח אם תוכלו לשלוח תמונות סרטונים או הערות נוספות שיכולו לעזור לנו')
        return 'more_media'

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
            user_data=full_user_data,
        )
        logger.info("Created chat report %d", chat_report.id)

    def save_user_info(self, chat_data_wrapper):
        if self.is_fb:
            full_user_data = self.get_fb_full_user_data()
        else:
            full_user_data = chat_data_wrapper.message.get('chat')

        self.session.report.user_data = full_user_data
        self.session.report.save()

    def get_fb_full_user_data(self):
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
